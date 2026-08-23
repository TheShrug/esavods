import { defineConfig } from 'vite';

/*
 |--------------------------------------------------------------------------
 | Asset build
 |--------------------------------------------------------------------------
 |
 | Replaces laravel-mix. With the dashboard gone there is no Vue and no SFC
 | handling left, so this only has to bundle one jQuery entry point and
 | compile one Sass file.
 |
 | Output filenames are deliberately unhashed. The Blade layout links
 | `js/app.js` and `css/app.css` through plain `asset()` helpers, and the
 | origin serves them `max-age=86400` without `immutable` precisely because
 | they are not fingerprinted. Emitting hashed names and a manifest would be a
 | change to the caching contract, not a build detail — so don't.
 |
 | jquery, bootstrap, popper.js and datatables.net are pinned to exact versions
 | in package.json — the ones the old lockfile resolved — so that regenerating
 | the lockfile for this build change doesn't silently bump them. Bumping them
 | is esavods#17.
 |
 */

export default defineConfig({
    // public/ is the web root, not a build artefact directory: index.php,
    // images and robots.txt live there. It is the output, so it must not also
    // be treated as a directory of files to copy into the output, and it must
    // never be emptied.
    publicDir: false,
    build: {
        outDir: 'public',
        emptyOutDir: false,
        manifest: false,
        rollupOptions: {
            input: 'resources/js/app.js',
            output: {
                entryFileNames: 'js/app.js',
                assetFileNames: 'css/[name][extname]',
            },
        },
    },
    css: {
        preprocessorOptions: {
            scss: {
                // Bootstrap 4.1 predates all of these. Bumping Bootstrap is
                // esavods#17; until then the warnings are noise that hides
                // real build output.
                silenceDeprecations: [
                    'import',
                    'if-function',
                    'global-builtin',
                    'color-functions',
                    'slash-div',
                ],
            },
        },
    },
});
