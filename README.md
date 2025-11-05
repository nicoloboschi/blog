# My Blog

A personal blog built with Hugo and deployed to GitHub Pages.

## Tech Stack

- **Static Site Generator**: [Hugo](https://gohugo.io/)
- **Theme**: [Chicago7](https://github.com/akopdev/hugo-theme-chicago7)
- **Hosting**: GitHub Pages
- **CI/CD**: GitHub Actions

## Local Development

### Prerequisites

- Hugo Extended version 0.152.2 or later
- Dart Sass (required for the Chicago7 theme)
- Git

### Installing Dart Sass

On macOS:
```bash
brew install sass/sass/sass
```

On other platforms, see [Dart Sass installation guide](https://gohugo.io/functions/css/sass/#dart-sass)

### Installation

1. Clone the repository with submodules:
```bash
git clone --recursive https://github.com/nicoloboschi/blog.git
cd blog
```

2. If you've already cloned without `--recursive`, initialize the submodules:
```bash
git submodule update --init --recursive
```

### Running Locally

Start the Hugo development server:

```bash
hugo server -D
```

The site will be available at `http://localhost:1313/blog/`

### Creating New Posts

Create a new blog post:

```bash
hugo new content posts/my-new-post.md
```

Edit the generated file in `content/posts/` and set `draft = false` when ready to publish.

## Deployment

The site automatically deploys to GitHub Pages when you push to the `main` branch.

### First-Time Setup

1. Go to your repository Settings → Pages
2. Under "Build and deployment", set Source to "GitHub Actions"
3. Push your changes to the `main` branch
4. The GitHub Actions workflow will build and deploy your site

Your site will be available at `https://nicoloboschi.github.io/blog/`

## Configuration

Edit `hugo.toml` to customize:
- Site title and description
- Base URL
- Theme colors
- Menu items
- And more

See the [Hugo documentation](https://gohugo.io/getting-started/configuration/) for all configuration options.

## License

This blog content is personal. The Hugo theme is licensed under MIT.
