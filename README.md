# Scriptor

> Scriptor was meanwhile superseded by [viur-scriptor](https://github.com/viur-framework/viur-scriptor). Please go there for an actively developed version.

Scriptor is a Python scripting environment for [ViUR](https://viur.dev) running in the browser.

## About

Scriptor can be used for custominzed analyzing, filtering, exporting or refining of any information provided from a VIUR-based system. It provides a set of pre-configured tools to easily access data from VIUR-modules, in-memory write data into CSV-files or output status information. This alltogether with the tools provided by Python's standard libary.

Scriptor is intended to be used by technically advised users for any kinds of tasks described above.

Scriptor uses the session of the user who is logged in, therefor logging into the ViUR-system before starting Scriptor is required.

Special thanks to [Andreas H. Kelch](https://github.com/XeoN-GHMB/) for doing [all the preliminary work](https://github.com/viur-framework/viur-vi/commit/89b2c7c5a1febceae0ac01982e45d0ebe37ffa7b) on this tool.

## Features

- Runs out-of-the-box on any ViUR project
- Editor with Python syntax highlighting (Codemirror 5.65.8)
- Python 3.10.2 running in a webworker (using Pyodide 0.21.2)
- Interaction protocol between the frontend and webworker
- `scripter.py` provides tools for
  - `viur` namespace to view and list modules
  - `csvwriter` class for in-memory CSV file writer
  - `logging` namespace for data output with several severities
  - `print()` function
  - `exit()` function
- Objects are JSON-serialized and pretty-printed for better readability

## Setup

To integrate Scriptor into your project either unpack a release or add scriptor as a submodule to your repository into the folder `deploy/scriptor`.

Then, add the following entry to your `app.yaml` handler section:

```yaml
- url: /scriptor
  static_dir: scriptor
```

Afterwards, you can access scriptor locally via `http://localhost:8080/scriptor/scriptor.html` or under the project URL when deployed from onto a specific app engine project.

Scriptor runs out of the box. It currently is limited to Chromium-based browsers only.

## License

Copyright © 2022 by Mausbrand Informationssysteme GmbH.<br>
Mausbrand and ViUR are registered trademarks of Mausbrand Informationssysteme GmbH.

MIT licensed. Please see the LICENSE file for details.
