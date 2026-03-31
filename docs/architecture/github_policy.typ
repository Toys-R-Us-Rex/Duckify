#import "@preview/codly:1.3.0": codly-init

#show: codly-init
#show link: set text(fill: blue)
#set text(font: "Source Sans 3")
#set heading(numbering: "1.1")

#align(
  center,
  text(size: 2em, weight: "bold")[Git / GitHub Policy]
)

= General

Git history should be kept semi-linear. Ideally, branches should be rebased before being merged. A simple merge commit is also accepted, as long as branch do not intertwine (i.e. merging A $->$ B and B $->$ A multiple times).

Force pushes are disallowed on shared branches unless discussed beforehand with affected people.

= Branches

Branch names should be prefixed by a type, for example:
- `feat/model-preview`: implements a new feature
- `fix/color-inversion`: fixes a bug or issue
- `refactor/migrate-to-postgres`: modifies the code structure without adding new features

If the branch is linked to an existing issue or task, the branch name should contain its reference. For example, `feat/JIRA-42-path-simplification`.

= Pull Requests

Branches must be merged into the `main` branch through a pull request. Pull requests should be kept relatively short and must be reviewed by at least one other person.
They must have a meaningful title, summarizing the features or fixes it contains, and can have a more in depth description to help reviewers understand the contents.
If a pull request is related to an existing issue or task, its title should contain its reference. For example, `JIRA-42: Path geometry simplification`.
A branch that has been merged must be deleted.

= Commits

== Content

A commit should be an atomic change targeting only 1 specific subject.

Build artifacts, cache directories, large files, personal configuration, environment variables and secrets must not be committed. If possible, such files should be added to `.gitignore` to avoid accidentally committing them.
External libraries, especially large packages, should either not be included in the repository (with installation steps), or integrated as Git submodules#footnote(link("https://github.blog/open-source/git/working-with-submodules/")).

== Message

Commit messages must follow the conventional commit format#footnote(link("https://www.conventionalcommits.org/en/v1.0.0/")). In short, commit messages must be structured as follows:
#figure(```
  <type>[optional scope]: <description>

  [optional body]

  [optional footer(s)]
  ```,
  caption: [Conventional commit message format]
)

The `type` element describes the content of the commit. The following values are accepted:
- `fix`: patches a bug / issue
- `feat`: introduces a new feature
- `doc` or `docs`: only affects documentation
- `chore`: small changes to the repository which does not directly affect code or documentation
- `ci`: modifies CI/CD workflow configuration
- `refactor`: modifies existing code without changing the results / features

Some other types can be accepted but the above list should suffice in most cases.

The description (or subject) should be kept short. An optional body can be added to provide more details.
It should be written in the imperative present tense:
- #emoji.checkmark.box `add database schema`
- #emoji.crossmark `changed path resolution`
- #emoji.crossmark `fixes rounding error`

The body can contain special keywords to indicate that it completes a specific issue or task, for example:
- `closes JIRA-123`
- `fixes #4`
- ...

== Authors

In cases where a commit is written by multiple people, footers can be added to indicate co-authors:

#figure(```
  feat: add segment data structures

  Co-Authored-By: John Doe <john.doe@example.com>
  ```,
  caption: [Simple co-author footer]
)

If a commit is partly written by an LLM, a footer must be added to name it as a co-author, for example:

#figure(```
  feat: add segment data structures

  Co-Authored-By: Claude <noreply@anthropic.com>
  ```,
  caption: [LLM co-author footer]
)

#align(right)[Louis Heredero]