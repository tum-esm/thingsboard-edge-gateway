Contributions
=============

This project is developed as **open-source scientific software** and welcomes
contributions from the community. Contributions range from documentation
improvements and bug fixes to architectural refinements and new functionality.

The project aims to provide a **reliable, reusable on-device gateway
infrastructure** for scientific sensor networks. Contributions that improve
robustness, clarity, and long-term maintainability are particularly valued.

This document describes the **recommended contribution process**.


Human-led Contributions and AI Usage
------------------------------------

This project welcomes contributions from **human contributors** only.

Automated or autonomous AI agents are **not permitted** to independently
open issues, submit pull requests, or participate in code review or
architectural discussions.

The use of AI-based tools (e.g. for drafting text, refactoring assistance,
or code suggestions) is acceptable **when used as a support tool by a human
contributor**, provided that:

- the contributor fully understands the proposed changes,
- the contributor takes responsibility for correctness, style, and impact,
- all contributions are reviewed, validated, and approved by a human.

Submissions that appear to be generated or maintained primarily by
autonomous agents may be closed without further review.


Contribution Workflow
---------------------

To keep development transparent and sustainable, most contributions follow an
**issue-first workflow**.

In general:

- Small documentation fixes may be submitted directly as pull requests.
- Bug fixes, new features, and refactoring efforts should start with a GitHub
  issue before code is written.

Starting with an issue helps:

- align expectations early,
- avoid duplicated work,
- discuss scope and design before implementation,
- document decisions for future contributors.


Choosing the Right Issue Type
-----------------------------

Please use the appropriate GitHub issue template when opening an issue.

Bug reports
^^^^^^^^^^^

Use the **Bug Report** template if you observe incorrect or unexpected behavior.

Typical examples:

- crashes or unhandled exceptions
- incorrect file synchronization behavior
- OTA update failures
- persistence or restart issues

Bug reports should include:

- steps to reproduce the issue
- relevant logs or error messages
- gateway version and device environment, if available


Feature requests
^^^^^^^^^^^^^^^^

Use the **Feature Request** template for user-facing changes or new capabilities.

Feature requests should:

- describe the **user-facing need first** (user story),
- outline a possible solution or approach (optional but helpful),
- indicate whether you would like to implement the feature yourself.

Feature requests are evaluated based on:

- alignment with project scope,
- impact on long-term maintainability,
- backward compatibility,
- operational robustness.


Refactoring and code cleanup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the **Refactoring / Code Cleanup** template for internal improvements that do
not introduce new user-facing features.

Typical refactoring proposals include:

- simplifying complex code paths,
- reducing duplication,
- clarifying module responsibilities,
- improving testability or maintainability.

Refactoring issues should clearly state:

- motivation for the change,
- affected components,
- confirmation that user-facing behavior remains unchanged (or describe changes).


Development Principles
----------------------

To keep the gateway reusable across research domains, contributions should
follow these principles:

- The gateway provides **infrastructure**, not application logic.
- Sensor- or domain-specific behavior belongs in the **external controller**.
- Changes should preserve:

  - robustness under intermittent connectivity,
  - unattended long-term operation,
  - clear separation of responsibilities.
- Backward compatibility should be maintained whenever feasible.

If a proposed change significantly affects architecture, persistence, or
external interfaces, please discuss it in an issue first.


Pull Requests
-------------

Once an issue has been discussed and agreed upon, you can proceed with a pull
request.

Recommended steps:

1. Fork the repository.
2. Create a feature branch from the main branch.
3. Implement the change with clear, focused commits.
4. Update documentation where relevant.
5. Open a pull request and link the related issue.

Pull requests should include:

- a short summary of the change,
- a reference to the related issue,
- notes on testing or validation,
- mention of any backward compatibility considerations.



Code Quality and Review
-----------------------

Contributions should aim to:

- follow the existing code structure and style,
- passing mypy checks,
- avoid unnecessary dependencies,
- keep behavior explicit and predictable.


Licensing and Acknowledgment
----------------------------

By contributing, you agree that your contributions will be released under the
project's open-source license.

All contributions are tracked through GitHub issues and acknowledged in the version release notes.


Getting Help
------------

If you are unsure whether a contribution fits the project or how to proceed:

- open an issue to discuss ideas or questions,
- ask for guidance in a draft pull request.

Early discussion is encouraged and helps ensure contributions are effective and
well-aligned.