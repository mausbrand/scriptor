window.addEventListener("load", () => {
    let worker = null;

    let output = document.querySelector("#output");
    let run = document.querySelector("#run");
    let stop = document.querySelector("#stop");

    // Initialize code editor
    editor = CodeMirror.fromTextArea(
        document.querySelector("#code"),
        {
            mode: "python",
            theme: "neo",
            lineNumbers: true,
            lineWrapping: true,
            styleActiveLine: true,
            styleActiveSelected: true,
            matchBrackets: true,
            keyMap: "sublime",
            smartIndent: true,
            indentUnit: 4,
            indentWithTabs: false,
            gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter", "CodeMirror-lint-markers"],
            foldGutter: true,
            autofocus: true,
            autorefresh: true,
            autoCloseBrackets: true
        }
    );

    function writeOutput(items, cls) {
        if (items === undefined) {
            return;
        }

        let li = document.createElement("li");

        if (cls) {
            li.className = cls;
        }

        li.innerText = items.join(" ");
        output.appendChild(li);
    }

    function eventHandler(event) {
        const data = event.data;
        console.debug(data);

        switch (data.type) {
            case "download":
                let a = document.createElement("a");
                a.href = URL.createObjectURL(data.blob);
                a.style["visible"] = "hidden";
                a.download = data.filename;

                document.body.appendChild(a)
                a.click()
                document.body.removeChild(a)
                break;

            case "error":
                stop.click();
                writeOutput(data.error, "error raw");
                break;

            case "exit":
                stop.click();
                break;

            case "print":
                writeOutput(data.items, data.level);
                break;

            case "result":
                stop.click();
                writeOutput(data.result);
                break;

            default:
                writeOutput(`${data.type} not implemented`, "error");
        }
    }

    run.addEventListener(
        "click", () => {
            if (worker !== null) {
                worker.terminate();
            }

            worker = new Worker("scriptor-worker.js");
            worker.onmessage = eventHandler;
            worker.onerrormessage = eventHandler;
            worker.postMessage({code: editor.getValue()});

            stop.disabled = false;
        }
    );

    clear.addEventListener(
        "click", () => {
            output.innerHTML = "";
        }
    );

    stop.addEventListener(
        "click", () => {
            worker.terminate();
            worker = null;
            stop.disabled = true;
        }
    );
});
