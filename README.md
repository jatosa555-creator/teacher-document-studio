# Teacher Document Studio

Create and improve editable Microsoft Word documents in Thai, English, or both. This package is designed for teachers and education teams preparing project reports, activity summaries, reflections, handouts, and academic documents.

The installable plugin contains the **Teacher Document Studio skill**. It provides document-specific instructions, sample layouts, and optional Python scripts. It does not connect to external services. Teachers do not need Python to use the skill through a ChatGPT environment that can read and create documents.

## Choose an installation path

### ChatGPT Skills: easiest for an individual teacher

1. Download [`dist/teacher-doc-studio-skill.zip`](dist/teacher-doc-studio-skill.zip).
2. In ChatGPT, open **Plugins → Skills → Create → Upload from your computer**.
3. Select the ZIP, review the scan, and install the skill.
4. Start a new chat, attach a Word document, and ask for the result in Thai or English.

Skill availability and uploading depend on the ChatGPT plan, workspace settings, and product availability. An administrator may need to enable skill uploading.

### ChatGPT workspace: install and sync from this GitHub repository

A workspace administrator can import this repository as a plugin marketplace:

1. Open **Admin → Plugins → Add → Import marketplace**.
2. Enter `https://github.com/jatosa555-creator/teacher-document-studio` as the source and leave Path blank.
3. Authorize GitHub access, import the marketplace, then make the plugin available to the intended teachers.

After that, teachers install **Teacher Document Studio** from their workspace's Plugins directory. GitHub marketplace import is an administrator workflow; a public GitHub repository alone does not automatically add the plugin to every ChatGPT account.

### Codex desktop or CLI

Add the GitHub marketplace and install the plugin:

```sh
codex plugin marketplace add jatosa555-creator/teacher-document-studio
codex plugin add teacher-doc-studio@teacher-document-studio
```

### Public ChatGPT and Codex plugin directory

This repository is the download and source repository. To make the plugin searchable in the universal OpenAI plugin directory, its owner must upload the plugin ZIP through the OpenAI plugin submission portal, complete identity and permission checks, pass skill scans, and receive review approval. Publishing this GitHub repository does not submit or publish that directory listing automatically.

## Ready-to-download packages

- [`teacher-doc-studio-skill.zip`](dist/teacher-doc-studio-skill.zip): upload from ChatGPT's Skills page.
- [`teacher-doc-studio-plugin.zip`](dist/teacher-doc-studio-plugin.zip): portable skills-only plugin package for local testing or OpenAI directory submission.

## What the skill does

- Formats Word reports using Thai, formal Thai, English, or bilingual profiles.
- Preserves supplied names, facts, scores, quotations, and source structure.
- Uses Word paragraph and heading styles, with guidance for tables, headers, footers, and page layout.
- Recommends rendering and visually checking every page when the environment supports it.
- Provides optional `python-docx` scripts for conservative styling and document-integrity checks.

The examples use fictional content. TH Sarabun New must be installed in the rendering environment to display that font as intended. The scripts are optional and run in the assistant's supported environment; teachers do not have to run them locally.

## Build the ZIP packages

With Python 3, run:

```sh
python scripts/package_release.py
```

The script packages the skill and plugin from `plugins/teacher-doc-studio/` into `dist/` and excludes Python cache files.

## Improve it

The layout profiles and examples are under `plugins/teacher-doc-studio/skills/teacher-doc-studio/`. Adjust the references, JSON profiles, and examples for a school's language, document types, and visual standards. Keep the skill instructions and both package manifests in sync when changing its name or version.

## License

No redistribution license has been selected for this initial release. The packages are shared for teachers to download and install for their document work. Please contact the project owner before redistributing or publishing modified copies.

---

## English installation notes

This is a **plugin that contains one reusable skill**. No separate connector or MCP server is needed for formatting documents that users attach to ChatGPT.

- **Individual ChatGPT users:** upload `dist/teacher-doc-studio-skill.zip` from **Plugins → Skills → Create → Upload from your computer**, when this feature is enabled for the account.
- **ChatGPT workspace admins:** import this GitHub repository at **Admin → Plugins → Add → Import marketplace**. Members can then install the plugin from their workspace directory.
- **Codex desktop or CLI:** add the repository as a marketplace using the commands above.
- **Universal public directory:** submit the plugin ZIP through OpenAI's review flow. GitHub hosting alone does not create a public directory listing.

Availability depends on the product surface, plan, and workspace settings.
