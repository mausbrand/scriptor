// scriptor-webworker.js

// THIS IS THE DEFAULT PYODIDE WEBWORKER
const PYODIDE_HOME = "https://cdn.jsdelivr.net/pyodide/v0.21.2/full/";
importScripts(PYODIDE_HOME + "pyodide.js");

async function loadPyodideAndPackages() {
    self.pyodide = await loadPyodide();
    //await self.pyodide.loadPackage(["numpy", "pytz"]);
}


let pyodideReadyPromise = loadPyodideAndPackages();


self.onmessage = async (event) => {
    // make sure loading is done
    await pyodideReadyPromise;

    // Don't bother yet with this line, suppose our API is built in such a way:
    const {code, ...context} = event.data;

    let response = await fetch("scriptor.py");
    let scriptor = await response.text();

    // The worker copies the context in its own "memory" (an object mapping name to values)
    for (const key of Object.keys(context)) {
        self[key] = context[key];
    }

    try {
        self.postMessage({
            type: "result",
            result: await self.pyodide.runPythonAsync(scriptor + code)
        });
    } catch (error) {
        console.log(error.message);
        self.postMessage({
            type: "error",
            error: error.message
        });
    }
}
