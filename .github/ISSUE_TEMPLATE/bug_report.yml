---
name: Bug report
description: Report a reproducible problem in the gateway
title: "[Bug]: "
labels: ["bug"]
assignees:
  - patrickjaigner
  - larsfroelich
body:
  - type: markdown
    attributes:
      value: |
        Thanks for reporting! Please include enough detail to reproduce the issue.

  - type: textarea
    id: summary
    attributes:
      label: Summary
      description: What happened and what did you expect?
      placeholder: "When ..., the gateway ..."
    validations:
      required: true

  - type: textarea
    id: repro
    attributes:
      label: Steps to reproduce
      description: Minimal, numbered steps.
      placeholder: |
        1. Configure ...
        2. Start ...
        3. Observe ...
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Logs / error output
      description: Paste relevant logs (redact secrets). Prefer a small excerpt + pointers.
      render: shell
    validations:
      required: false

  - type: input
    id: version
    attributes:
      label: Gateway version / commit
      placeholder: "vX.Y.Z or commit hash"
    validations:
      required: false

  - type: input
    id: platform
    attributes:
      label: Device / OS
      placeholder: "Raspberry Pi 4, Debian 12, Python 3.12"
    validations:
      required: false

  - type: textarea
    id: config
    attributes:
      label: Relevant configuration
      description: Include only relevant snippets (redact tokens).
      render: yaml
    validations:
      required: false

  - type: dropdown
    id: impact
    attributes:
      label: Impact
      options:
        - minor (cosmetic / low frequency)
        - moderate (workaround exists)
        - major (blocks operation / data loss risk)
    validations:
      required: true
