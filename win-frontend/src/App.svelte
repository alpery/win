<script>
    import {onMount} from "svelte";

    // State variables
    let city = "Heilbronn";
    let weatherData = [];
    let loading = false;
    let error = null;
    let dailyForecasts = [];
    let selectedDayIndex = 0;
    let recentSearches = [];
    let showRecentSearches = false;
    let isConnected = true;
    let isRecording = false;
    let triggerWord = "Wetter";

    let days = 5;
    let lang = 'de';
    // Voice recognition variables
    let recognition = null;
    let isListening = false;
    let voicePrompt = "";
    let inputRef = null;
    let showVoiceHint = true;


    //anoimation variablen

    let drops = Array.from({length: 100});

    // Function to fetch weather data
    async function fetchWeatherData() {

        if (!city.trim()) {
            city = "Please enter a city name";
            return;
        }

        loading = true;
        error = null;

        try {
            console.log(city)
            const response = await fetch(
                `http://localhost:8080/api/weather/${city}`,
            );

            if (!response.ok) {
                throw new Error(
                    `Failed to fetch weather data: ${response.statusText}`,
                );
            }

            weatherData = await response.json();
            processWeatherData();
            dailyForecasts[0].description = "rain";


        } catch (err) {
            console.error("Error fetching weather data:", err);
            error = `Error fetching weather data: ${err.message}`;
            weatherData = [];
            dailyForecasts = [];

        } finally {
            loading = false;
        }
    }

    // Process weather data to group by day
    function processWeatherData() {


        if (!weatherData || weatherData.length === 0) {
            dailyForecasts = [];
            return;
        }

        // Group forecasts by day
        const groupedByDay = {};

        weatherData.forEach((item) => {
            const date = new Date(item.forecastDate);
            const dayKey = date.toISOString().split("T")[0]; // YYYY-MM-DD format

            if (!groupedByDay[dayKey]) {
                groupedByDay[dayKey] = [];
            }

            groupedByDay[dayKey].push(item);
        });

        // Create daily summary for each day
        dailyForecasts = Object.keys(groupedByDay)
            .map((day) => {
                const forecasts = groupedByDay[day];
                const dayData = forecasts[0]; // Use first forecast for basic info
                const currentTemp = dayData.temperature
                // Find min and max temperatures for the day
                const minTemp = Math.min(
                    ...forecasts.map((f) => f.minTemperature),
                );
                const maxTemp = Math.max(
                    ...forecasts.map((f) => f.maxTemperature),
                );

                // Calculate average humidity
                const avgHumidity = Math.round(
                    forecasts.reduce((sum, f) => sum + f.humidity, 0) /
                    forecasts.length,
                );

                // Get the noon forecast if available, otherwise use the first one
                const noonForecast =
                    forecasts.find((f) => {
                        const date = new Date(f.forecastDate);
                        return date.getHours() >= 12 && date.getHours() < 15;
                    }) || dayData;

                // Get weather condition category
                const weatherCondition = getWeatherCondition(
                    noonForecast.description,
                );

                // Filter out forecasts with duplicate formatted times
                const uniqueForecasts = [];
                const seenTimes = new Set();

                // Sort forecasts by time first
                const sortedForecasts = forecasts.sort(
                    (a, b) => new Date(a.forecastDate) - new Date(b.forecastDate)
                );

                // Keep only one forecast per formatted time
                sortedForecasts.forEach(forecast => {
                    const formattedTime = new Date(forecast.forecastDate).toLocaleTimeString("de-DE", {
                        hour: "2-digit",
                        minute: "2-digit",
                    });

                    if (!seenTimes.has(formattedTime)) {
                        seenTimes.add(formattedTime);
                        uniqueForecasts.push(forecast);
                    }
                });

                return {
                    date: new Date(day),
                    city: dayData.city,
                    temperature: currentTemp,
                    minTemperature: minTemp,
                    maxTemperature: maxTemp,
                    avgHumidity: avgHumidity,
                    description: noonForecast.description,
                    iconCode: noonForecast.iconCode,
                    weatherCondition: weatherCondition,
                    forecasts: uniqueForecasts, // Use filtered forecasts without duplicates
                };
            })
            .sort((a, b) => a.date - b.date); // Sort by date

        // Reset selected day to first day
        selectedDayIndex = 0;
        city = dailyForecasts[0].city
    }

    // Get weather condition category
    function getWeatherCondition(description) {
        const desc = description.toLowerCase();
        if (desc.includes("klar") || desc.includes("himmel")) return "clear";
        if (desc.includes("wolke") || desc.includes("bewölkt")) return "cloudy";
        if (desc.includes("regen")) return "rain";
        if (desc.includes("schnee")) return "snow";
        if (desc.includes("gewitter") || desc.includes("sturm")) return "storm";
        if (desc.includes("nebel")) return "fog";
        return "default";
    }


    // Format date to display full date
    function formatDate(date) {
        return new Date(date).toLocaleDateString("de-DE", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
        });
    }


    // Get weather icon URL
    function getWeatherIconUrl(iconCode) {
        return `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
    }

    // Handle form submission
    function handleSubmit(event) {
        event.preventDefault();
        fetchWeatherData();
        showRecentSearches = false;
    }


    // Select a recent search
    function selectRecentSearch(searchTerm) {
        city = searchTerm;
        fetchWeatherData();
        showRecentSearches = false;
    }

    // Get background gradient based on time and weather
    function getBackgroundGradient(forecast) {
        if (!forecast) return "linear-gradient(to bottom, #4b6cb7, #182848)";

        const condition = forecast.weatherCondition;
        const hour = new Date(forecast.forecasts[0].forecastDate).getHours();
        const isDay = hour >= 6 && hour < 20;

        if (condition === "clear") {
            return isDay
                ? "linear-gradient(to bottom, #2980b9, #6dd5fa, #ffffff)"
                : "linear-gradient(to bottom, #0f2027, #203a43, #2c5364)";
        } else if (condition === "cloudy") {
            return isDay
                ? "linear-gradient(to bottom, #757f9a, #d7dde8)"
                : "linear-gradient(to bottom, #373b44, #4286f4)";
        } else if (condition === "rain") {
            return "linear-gradient(to bottom, #616161, #9bc5c3)";
        } else if (condition === "snow") {
            return "linear-gradient(to bottom, #e6dada, #274046)";
        } else if (condition === "storm") {
            return "linear-gradient(to bottom, #232526, #414345)";
        } else if (condition === "fog") {
            return "linear-gradient(to bottom, #b79891, #94716b)";
        }

        return "linear-gradient(to bottom, #4b6cb7, #182848)";
    }


    function setupSpeechRecognition() {
        if (typeof window === 'undefined') return;

        try {
            // @ts-ignore
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                console.log("Speech Recognition not supported");
                return;
            }

            recognition = new SpeechRecognition();
            recognition.lang = lang === 'de' ? 'de-DE' : 'en-US';
            recognition.continuous = false;

            recognition.onstart = () => isRecording = true;
            recognition.onend = () => {
                isRecording = false;
                if (isListening) {
                    setTimeout(() => recognition.start(), 300);
                }
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript.toLowerCase();
                console.log("Heard:", transcript);

                if (!transcript.includes(triggerWord.toLowerCase())) return;

                // Extract command after trigger word
                const parts = transcript.split(triggerWord.toLowerCase());
                if (parts.length < 2) return;

                let command = parts[1].trim()
                if (command.endsWith('.')) {
                    command = command.slice(0, -1);
                }
                if (!command) return;
                command = command.replace(/\.$/, '');
                if (!command) return;

                // Parse command
                parseVoiceCommand(command);
            };

            isListening = true;
            recognition.start();
        } catch (e) {
            console.error("Speech recognition error:", e);
        }
    }

    function parseVoiceCommand(command) {
        // Extract city and days from command
        const words = command.trim().split(/\s+/);
        let newDays = 5;
        let cityWords = [];

        for (let i = 0; i < words.length; i++) {
            const num = parseInt(words[i]);
            if (!isNaN(num)) {
                newDays = Math.min(Math.max(num, 1), 5); // Limit between 1-5
            } else {
                cityWords.push(words[i]);
            }
        }

        const newCity = cityWords.join(" ").trim();
        if (newCity) {
            city = newCity;
            days = newDays;
            fetchWeatherData();
        }
    }

    function checkConnection() {
        isConnected = navigator.onLine;
        window.addEventListener('online', () => isConnected = true);
        window.addEventListener('offline', () => isConnected = false);
    }


    // Initialize with a default city and load recent searches
    onMount(() => {
        // Load recent searches from localStorage

        setupSpeechRecognition();
        checkConnection();

        document.getElementsByClassName("city-input").value = (" ")

        // Start with a default city

        fetchWeatherData();

        // Initialize speech recognition

    });

    // Get today's date in the same format as your forecast date

    // Function to check if the weather data corresponds to today


</script>
<main>
    <div class="weather-animation">
        {#if dailyForecasts.length > 0 && dailyForecasts[selectedDayIndex].weatherCondition === 'rain'}
            <div class="rain-animation">
                {#each drops as _, i}
                    <div class="drop" style="left: {Math.random() * 100}%; animation-delay: {Math.random()}s;"></div>
                {/each}
            </div>
        {/if}
    </div>


    {#if dailyForecasts.length > 0}
        <div class="weather-app" style="background: {getBackgroundGradient(dailyForecasts[selectedDayIndex])}">
            <div class="app-header">
                <h1>Wetter Vorhersage</h1>

                <div class="voice-hint">
                    <div class="voice-hint-content">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
                             fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                             stroke-linejoin="round">
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                            <line x1="12" y1="19" x2="12" y2="23"></line>
                            <line x1="8" y1="23" x2="16" y2="23"></line>
                        </svg>
                        <span>Neu! Sprachsteuerung verfügbar. Sagen Sie "Wetter" und irgendwelche Stadt</span>
                    </div>
                </div>
                <div class="status-indicators">
                    <div class="connection-status {isConnected ? 'connected' : 'disconnected'}">
                        {isConnected ? '🟢 Verbunden' : '🔴 Nicht verbunden'}
                    </div>
                    <div class="recording-status {isRecording ? 'recording' : ''}">
                        {isRecording ? '🎤 Aufnahme läuft...' : '🎤 Bereit für Sprachbefehle'}
                    </div>
                </div>


                <div class="search-container">
                    <form on:submit={handleSubmit} class="search-form">
                        <div class="input-wrapper {isListening ? 'listening' : ''}">
                            <input type="text" bind:value={city} bind:this={inputRef}
                                   placeholder={isListening ? voicePrompt : "Stadt eingeben..."} class="city-input"
                                   on:focus={() => (showRecentSearches = true)}/>
                            {#if showRecentSearches && recentSearches.length > 0}
                                <div class="recent-searches">
                                    {#each recentSearches as search}
                                        <div class="recent-search-item" role="button"
                                             on:click={() => selectRecentSearch(search)}
                                             on:keydown={(e) => e.key === "Enter" && selectRecentSearch(search)}
                                             tabindex="0">
                                            {search}
                                        </div>
                                    {/each}
                                </div>
                            {/if}
                        </div>
                    </form>
                </div>
            </div>

            {#if error}
                <div class="error-message">
                    {error}
                </div>
            {/if}

            {#if loading}
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Wetterdaten werden geladen...</div>
                </div>
            {:else}
                <div class="today-weather-card">
                    <div class="date">{formatDate(dailyForecasts[0].date)}</div>

                    <div class="weather-info">
                        <div class="temperature-container">
                            <div class="current-temp">{Math.round(dailyForecasts[0].temperature)}°C</div>
                            <div class="min-max">
                                <span class="min">{Math.round(dailyForecasts[0].minTemperature)}°C</span> /
                                <span class="max">{Math.round(dailyForecasts[0].maxTemperature)}°C</span>
                            </div>
                        </div>

                        <div class="weather-icon">
                            <img src={getWeatherIconUrl(dailyForecasts[0].iconCode)}
                                 alt={dailyForecasts[0].description}/>
                            <div class="description">{dailyForecasts[0].description}</div>
                        </div>
                    </div>

                    <div class="details">
                        <div class="detail-item">
                            <span class="label">Luftfeuchtigkeit:</span>
                            <span class="value">{dailyForecasts[0].avgHumidity}%</span>
                        </div>
                    </div>
                </div>


                <div class="next-weather">
                    <!-- Here is where the first weather card logic comes in -->
                    {#each dailyForecasts.slice(1) as weatherData}

                        <div class="weather-card">
                            <div class="date">{formatDate(weatherData.date)}</div>

                            <div class="weather-info">
                                <div class="temperature-container">
                                    <div class="current-temp">{Math.round(weatherData.temperature)}°C</div>
                                    <div class="min-max">
                                        <span class="min">{Math.round(weatherData.minTemperature)}°C</span> /
                                        <span class="max">{Math.round(weatherData.maxTemperature)}°C</span>
                                    </div>
                                </div>

                                <div class="weather-icon">
                                    <img src={getWeatherIconUrl(weatherData.iconCode)} alt={weatherData.description}/>
                                    <div class="description">{weatherData.description}</div>
                                </div>
                            </div>

                            <div class="details">
                                <div class="detail-item">
                                    <span class="label">Luftfeuchtigkeit:</span>
                                    <span class="value">{weatherData.avgHumidity}%</span>
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    {:else if !loading && !error}
        <div class="weather-app empty-state">
            <div class="app-header">
                <h1>Wetter Vorhersage</h1>

                {#if showVoiceHint}
                    <div class="voice-hint">
                        <div class="voice-hint-content">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
                                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                 stroke-linejoin="round">
                                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                                <line x1="12" y1="19" x2="12" y2="23"></line>
                                <line x1="8" y1="23" x2="16" y2="23"></line>
                            </svg>
                            <span>Neu! Sprachsteuerung verfügbar. Sagen Sie "Konrad" oder klicken Sie auf das Mikrofon-Symbol, um nach einer Stadt zu suchen.</span>
                        </div>
                    </div>
                {/if}

                <div class="search-container">
                    <form on:submit={handleSubmit} class="search-form">
                        <div class="input-wrapper {isListening ? 'listening' : ''}">
                            <input class="city-input" type="text" bind:value={city} bind:this={inputRef}
                                   placeholder={isListening ? voicePrompt : "Stadt eingeben..."}
                                   on:focus={() => (showRecentSearches = true)}/>
                            {#if showRecentSearches && recentSearches.length > 0}
                                <div class="recent-searches">
                                    {#each recentSearches as search}
                                        <div class="recent-search-item" role="button"
                                             on:click={() => selectRecentSearch(search)}
                                             on:keydown={(e) => e.key === "Enter" && selectRecentSearch(search)}
                                             tabindex="0">
                                            {search}
                                        </div>
                                    {/each}
                                </div>
                            {/if}
                        </div>
                    </form>
                </div>
            </div>

            {#if error}
                <div class="error-message">
                    {error}
                </div>
            {/if}

            {#if loading}
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Wetterdaten werden geladen...</div>
                </div>
            {:else}
                <div class="no-data">
                    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"></path>
                    </svg>
                    <p>Keine Wetterdaten verfügbar. Bitte suchen Sie nach einer Stadt.</p>
                </div>
            {/if}
        </div>
    {/if}
</main>

<style>
    .rain-animation {
        animation: rain 2s infinite;
    }

    @keyframes rain {
        0% {
            opacity: 0;
        }
        50% {
            opacity: 1;
        }
        100% {
            opacity: 0;
        }
    }

    .weather-animation {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        overflow: hidden;
        z-index: 1;
    }

    .rain-animation .drop {
        position: absolute;
        top: -10%;
        width: 2px;
        height: 20px;
        background: rgba(255, 255, 255, 0.5);
        animation: rainDrop 0.7s linear infinite;
    }

    @keyframes rainDrop {
        0% {
            transform: translateY(0);
            opacity: 1;
        }
        100% {
            transform: translateY(120vh);
            opacity: 0;
        }
    }


    .rain-animation::before {
        content: "";
        position: absolute;
        top: -100%;
        left: 50%;
        width: 2px;
        height: 100%;
        background: rgba(255, 255, 255, 0.5);
        animation: rainDrop 0.5s linear infinite;
    }

    @keyframes rainDrop {
        0% {
            transform: translateY(0);
            opacity: 1;
        }
        100% {
            transform: translateY(100vh);
            opacity: 0;
        }
    }


    .connection-status, .recording-status {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }

    .connected {
        background-color: #48bb78; /* Grüner Hintergrund */
        color: #2f855a;
    }

    .disconnected {
        background-color: #f56565; /* Roter Hintergrund */
        color: #c53030;
    }

    .recording {
        background-color: #f56565; /* Pinker Hintergrund */
        color: #b83280;
        animation: pulse 1.5s infinite;

    }


    .status-indicators {
        display: flex;
        font-size: 1.5rem;
        justify-content: center;
        gap: 1.5rem;
        margin-top: 0.5rem;
        padding: 12px 15px;
        border: none;
        border-radius: 25px;
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        text-align: center;
        justify-self: center;
    }

    :global(body) {
        margin: 0;
        padding: 0;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f5f5f5;
        color: #333;
    }

    :global(*) {
        box-sizing: border-box;
    }

    main {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }

    .weather-app {
        width: 100%;
        min-height: 100vh;
        padding: 20px;
        transition: background 0.5s ease;
        color: white;
        display: flex;
        flex-wrap: wrap;
        flex-direction: column;
        justify-content: space-around;
    }

    .empty-state {
        background: linear-gradient(to bottom, #4b6cb7, #182848);
    }

    .app-header {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 30px;
        flex-wrap: wrap;
        gap: 20px;
        flex-direction: column;
    }

    .next-weather {

        display: flex;
        flex-wrap: wrap; /* Erlaubt den Umbruch, wenn der Platz nicht ausreicht */
        justify-content: space-evenly; /* Verteilt den Platz gleichmäßig */
        gap: 20px; /* Abstand zwischen den Karten */
        padding: 20px;
    }

    .weather-card {
        font-size: large;
        text-align: center;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s;
    }

    .today-weather-card {
        font-size: x-large;

        text-align: center;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s;

    }

    .current-temp {
        margin-top: 10px;
        justify-self: center;
    }

    .today-weather-card:hover {
        transform: translateY(-5px);
    }


    h1 {
        margin: 0;
        font-size: 4rem;
        font-weight: 700;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
        justify-content: center;
        text-align: center;
    }

    h2 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }

    h3 {
        margin: 20px 0 15px;
        font-size: 1.3rem;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }

    .search-container {
        position: relative;
    }

    .search-form {
        display: flex;
        gap: 10px;
    }

    .input-wrapper {
        position: relative;
    }

    .city-input {
        font-size: 3rem;
        padding: 12px 15px;
        border: none;
        border-radius: 25px;
        width: 450px;
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        text-align: center;
    }

    .city-input::placeholder {
        color: rgba(255, 255, 255, 0.7);
    }

    .city-input:focus {
        outline: none;
        background-color: rgba(255, 255, 255, 0.3);
        box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.5);
    }

    .recent-searches {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-top: 5px;
        z-index: 10;
        overflow: hidden;
    }

    .recent-search-item {
        padding: 10px 15px;
        cursor: pointer;
        color: #333;
        transition: background-color 0.2s;
    }

    .recent-search-item:hover {
        background-color: #f5f5f5;
    }


    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(255, 100, 100, 0.5);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(255, 100, 100, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(255, 100, 100, 0);
        }
    }

    .voice-hint {
        width: 100%;
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        animation: fadeIn 0.5s ease-out;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .voice-hint-content {
        display: flex;
        align-items: center;
        text-align: center;
        gap: 10px;
    }

    .voice-hint-content svg {
        flex-shrink: 0;
    }

    .error-message {
        color: #fff;
        text-align: center;
        margin: 20px auto;
        padding: 12px 15px;
        background-color: rgba(220, 53, 69, 0.8);
        border-radius: 8px;
        max-width: 600px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 50px 0;
        gap: 20px;
    }

    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 5px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .loading-text {
        font-size: 1.1rem;
        color: white;
    }

    .no-data {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 50px auto;
        color: white;
        text-align: center;
        gap: 20px;
    }

    .no-data svg {
        opacity: 0.8;
    }

    .no-data p {
        font-size: 1.2rem;
        max-width: 400px;
    }


    .current-temp-icon img {
        width: 100px;
        height: 100px;
        filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.4));
    }

    .current-temp {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 10px;
    }


    @media (min-width: 1024px) {
        .next-weather {
            text-align: center;
        }

        .weather-card {
            text-align: center;
        }

        .today-weather-card {
            text-align: center;

        }
    }

    /* Für kleine Bildschirme */
    @media (max-width: 1023px) {
        .next-weather {
            justify-content: center; /* Karten zentrieren */
        }

        .app-header {
            align-items: stretch;
            text-align: center;
        }

        .next-weather {
            text-align: center;
        }

        .weather-card {
            text-align: center;
        }

        .today-weather-card {
            text-align: center;

        }

    }

    @media (max-width: 768px) {
        .app-header {
            align-items: stretch;
            text-align: center;
        }


        .current-temp {
            justify-content: center;
            text-align: center;

        }


        .city-input {
            width: 100%;
            padding: 12px 15px;
            font-size: 2rem;
            border: none;
            border-radius: 25px;
            background-color: rgba(255, 255, 255, 0.2);
            color: white;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .search-form {
            width: 100%;
        }

        .input-wrapper {
            flex: 1;
        }

        .next-weather {
            text-align: center;
        }

        .weather-card {
            text-align: center;
        }

        .today-weather-card {
            text-align: center;

        }

    }

    @media (max-width: 480px) {
        .weather-app {
            padding: 15px;
            text-align: center;

        }

        h1 {
            font-size: 1.5rem;
        }

        h2 {
            font-size: 1.3rem;
        }

        .next-weather {
            text-align: center;
        }

        .weather-card {
            text-align: center;
        }

        .today-weather-card {
            text-align: center;

        }


    }


    .weather-card:hover {
        transform: translateY(-5px);
    }


</style>
