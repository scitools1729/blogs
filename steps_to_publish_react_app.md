# Steps to Publish React App to GitHub Pages

Here are the precise step-by-step instructions to host your Vite React application (`mod-llmesh-hub-ui/web`) on GitHub Pages using GitHub Actions.

## Step 1: Update your Vite Configuration

If you are deploying your site to a GitHub project repository (e.g., `https://<USERNAME>.github.io/<REPO-NAME>/`), you need to specify the base path in your Vite configuration.

Open `mod-llmesh-hub-ui/web/vite.config.js` and update it to add the `base` property matching your repository name. Assuming your GitHub repository is named `llmesh`, it should look like this:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/<YOUR-REPO-NAME>/', // Replace with your exact repository name, e.g., '/llmesh/'
})
```
*(If you are deploying to a user/organization page e.g., `https://<USERNAME>.github.io/` without a subpath, you can skip this step or set `base: '/'`).*

## Step 2: Create a GitHub Actions Workflow

We'll create an automatic deployment pipeline. Whenever you push to the `main` branch, it will build your application and deploy it to GitHub Pages.

1. Ensure your current project is pushed to a GitHub repository.
2. At the very root of your project repository (not just inside the `web` folder), create the directory structure: `.github/workflows/`.
3. Create a new file named `deploy.yml` inside that directory with the following content:

```yaml
name: Deploy React App to GitHub Pages

on:
  # Runs on pushes targeting the default branch
  push:
    branches: ["main"]

  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

# Sets permissions of the GITHUB_TOKEN to allow deployment to GitHub Pages
permissions:
  contents: read
  pages: write
  id-token: write

# Allow only one concurrent deployment, skipping runs queued between the run in-progress and latest queued.
# However, do NOT cancel in-progress runs as we want to allow these production deployments to complete.
concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  # Build job
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
          cache-dependency-path: mod-llmesh-hub-ui/web/package-lock.json
          
      - name: Install dependencies
        working-directory: ./mod-llmesh-hub-ui/web
        run: npm ci
        
      - name: Build
        working-directory: ./mod-llmesh-hub-ui/web
        run: npm run build
        
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          # Upload the compiled dist folder
          path: ./mod-llmesh-hub-ui/web/dist

  # Deployment job
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    needs: build
    runs-on: ubuntu-latest
    name: Deploy
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

*Note: If your main branch is called `master` rather than `main`, update line 7 to `branches: ["master"]`.*

## Step 3: Commit and Push

Commit those changes to your repository and push them to GitHub.

```bash
git add .
git commit -m "Add GitHub Pages deployment workflow"
git push origin main
```

## Step 4: Configure GitHub Repository Settings

1. Go to your repository on GitHub.
2. Click on **Settings**.
3. On the left sidebar, click on **Pages**.
4. Under the **Build and deployment** section, look for **Source**.
5. Change the dropdown option from "Deploy from a branch" to **"GitHub Actions"**.

## Step 5: Wait for Deployment

Go to your repository's **Actions** tab on GitHub. You should see your new workflow "Deploy React App to GitHub Pages" running. Once it turns green, your project is officially hosted! GitHub will provide the live URL directly on the right side of your repository homepage, under "Environments" -> "github-pages".
