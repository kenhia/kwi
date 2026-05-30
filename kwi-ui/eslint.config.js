import js from "@eslint/js";
import ts from "typescript-eslint";
import svelte from "eslint-plugin-svelte";
import globals from "globals";

/** @type {import('eslint').Linter.Config[]} */
export default [
  js.configs.recommended,
  ...ts.configs.recommended,
  ...svelte.configs["flat/recommended"],
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
    },
  },
  {
    files: ["**/*.svelte", "**/*.svelte.ts", "**/*.svelte.js"],
    languageOptions: {
      parserOptions: {
        parser: ts.parser,
      },
    },
    rules: {
      // Bare reactive references inside $effect (e.g. `projectId;`) are an
      // intentional Svelte 5 runes idiom for registering dependencies, not
      // dead expressions.
      "@typescript-eslint/no-unused-expressions": "off",
    },
  },
  {
    ignores: [
      "build/",
      ".svelte-kit/",
      "src-tauri/",
      "static/",
      "node_modules/",
    ],
  },
];
