# Win Frontend

A Svelte 5 application built with Vite.

## Installation

This project uses [pnpm](https://pnpm.io/) as the package manager. If you don't have pnpm installed, you can install it using:

```bash
npm install -g pnpm
```

To install the project dependencies:

```bash
# Clone the repository
git clone <repository-url>
cd win-frontend

# Install dependencies
pnpm install
```

## Running the Application

### Development Mode

To run the application in development mode with hot module replacement:

```bash
pnpm dev
```

This will start the development server at `http://localhost:5173` (default Vite port).

### Building for Production

To build the application for production:

```bash
pnpm build
```

This will generate optimized assets in the `dist` directory.

### Previewing the Production Build

To preview the production build locally:

```bash
pnpm preview
```

## Recommended IDE Setup

### WebStorm

[WebStorm](https://www.jetbrains.com/webstorm/) provides excellent support for Svelte and JavaScript projects. To set up WebStorm for this project:

1. Install WebStorm from the [JetBrains website](https://www.jetbrains.com/webstorm/download/)
2. Install the Svelte plugin:
   - Go to Preferences/Settings > Plugins
   - Search for "Svelte" and install the official plugin
3. Configure JavaScript settings:
   - Go to Preferences/Settings > Languages & Frameworks > JavaScript
   - Set JavaScript language version to "ECMAScript 6+"
   - Enable "ESM" for module system

WebStorm will automatically recognize the project's configuration from `jsconfig.json` and provide appropriate code assistance.

## Technical Considerations

**Why use this over SvelteKit?**

- It brings its own routing solution which might not be preferable for some users.
- It is first and foremost a framework that just happens to use Vite under the hood, not a Vite app.

This template contains as little as possible to get started with Vite + Svelte, while taking into account the developer experience with regards to HMR and intellisense. It demonstrates capabilities on par with the other `create-vite` templates and is a good starting point for beginners dipping their toes into a Vite + Svelte project.

Should you later need the extended capabilities and extensibility provided by SvelteKit, the template has been structured similarly to SvelteKit so that it is easy to migrate.

**Why is HMR not preserving my local component state?**

HMR state preservation comes with a number of gotchas! It has been disabled by default in both `svelte-hmr` and `@sveltejs/vite-plugin-svelte` due to its often surprising behavior. You can read the details [here](https://github.com/sveltejs/svelte-hmr/tree/master/packages/svelte-hmr#preservation-of-local-state).

If you have state that's important to retain within a component, consider creating an external store which would not be replaced by HMR.

```js
// store.js
// An extremely simple external store
import { writable } from 'svelte/store'
export default writable(0)
```
