# Contributing to the Verifiable Software Project

Thanks for your interest in contributing to our work! Please review these guidelines to help us make this project successful.

## Using Git

All work should be done on a feature branch. No users should push directly to the main branch. We will use pull requests to merge code from these feature branches into the main branch. A pull request must be approved by an authorized reviewer, and pass the automated testing, before being merged into the main branch.

## Issues

In general, all changes should be based on an [issue](https://github.com/verifiablesoftware/vsw/issues). If you would like to work on an existing issue, first check if anyone is already assigned and if so, discuss with that person before beginning work. If you would like to work on a new problem or enhancement, first create an issue for it and discuss with the community. The best way to do this will be to [join us in Slack](https://forms.office.com/Pages/ResponsePage.aspx?id=8o_uD7KjGECcdTodVZH-3OiciJKG_BJHrqMNgnsFFqtUOVZLWlhMTDJLVUxYTk1UWFBOSkMzM0pESy4u).

When creating a new issue, please be descriptive and include all relevant details, enough that someone completely unfamiliar with the problem or proposal can understand. Be sure to label your issue with the appropriate category (bug, enhancement, documentation, etc.). If you plan to work on the issue yourself, feel free to self-assign, otherwise, you can leave it unassigned for someone else to pick up.

If you plan to begin work on an issue, first verify that it is not already assigned to someone else. If it is already assigned, but you have some special reason to work on this issue, be sure to communicate with the assigned person. If it is unassigned, assign it to yourself before beginning work so that others know you are working on it. Use the issues comments to update your status regularly and communicate any important information to the community.

## Using Git

In order to keep a clean, easy to follow history, using git properly is important. The commit message should follow a particular format to make it easy to read and understand when someone reviews it in the future. The article, ["How to Write a Git Commit Message"](https://chris.beams.io/posts/git-commit/) does a great job of explaining how and why to write a good message. The key points are:

1. Separate subject from body with a blank line
2. Limit the subject line to 50 characters
3. Capitalize the subject line (first word, like a sentence)
4. Do not end the subject line with a period
5. Use the imperative mood in the subject line
6. Wrap the body at 72 characters
7. Use the body to explain what and why vs. how

Many editors will have plugins or settings to help you with the formatting of these messages.

If your commit is related to or closes an issue, be sure to include a line like this at the end of your message, and GitHub will automatically link it with the issue and/or close the issue:

```
See #23
Resolves #45
```

## Submitting your Changes

This project uses the standard GitHub mechanism for pull requests. See ["GitHub: Contributing to a Project"](https://git-scm.com/book/en/v2/GitHub-Contributing-to-a-Project) for the basic information on how to fork the repository, create a pull request, etc.

Checklist before opening your PR to save time and avoid unnecessary back and forth:
- [ ] Use [Prettier](https://prettier.io/) to format your code with the standard style for consistency and ease of reading; There is likely a plugin for whatever IDE you may use
- [ ] Run the testsuite locally before opening your PR
- [ ] Squash your commmits into logical units and write properly formatted commit messages (see [Using Git](#using-git) above)
- [ ] Does this changeset include any significant changes? If so, be sure to include a change to *CONTRIBUTING.md* in your branch.

All pull requests must be reviewed and approved by at least one owner before being accepted. Please also review ["Using Git"](using-git) and ensure that your commit messages follow the guidelines laid out there.

## Contributing to the Documentation

The documentation for this project is also stored in the repository, so we follow the same procedures for making changes to it. You may open issues against documentation, in the same way you would do for issues with the code. Documentation is important for new and future developers and users, so this is another vital part of any project. Details about design and implementation details should be added into the *docs/design/* directory.
