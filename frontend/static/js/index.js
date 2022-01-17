function update_tracing_tree() {
    var toggler = document.getElementsByClassName("tracer_name");
    var i;

    for (i = 0; i < toggler.length; i++) {
        toggler[i].addEventListener("click", function () {
            this.parentElement.querySelector(".nested").classList.toggle("active");
            this.classList.toggle("tracer_name-down");
        });
    }

    toggler = document.getElementsByClassName("tracer_run");

    for (i = 0; i < toggler.length; i++) {
        toggler[i].addEventListener("click", function (event) {
            // this.parentElement.querySelector(".nested").classList.toggle("active");
            // this.classList.toggle("tracer_name-down");
            load_run_info(event.target.uuid);
        });
    }
}

function add_tracer_run(value) {
    var new_span = document.createElement("span");
    new_span.setAttribute("class", "tracer_name");
    new_span.textContent = value["tracer_name"];
    var new_li = document.createElement("li");
    new_li.appendChild(new_span);

    var new_ul = document.createElement("ul");
    new_ul.setAttribute("class", "nested");

    $.each(value["runs"], function (index, run_data) {
        var run_li = document.createElement("li");
        run_li.setAttribute("class", "tracer_run");
        run_li.innerHTML = run_data["creation_time"];
        run_li.uuid = run_data["uuid"];
        new_ul.appendChild(run_li);
    });
    new_li.appendChild(new_ul);
    $(tracer_tree_ctrl).append(new_li)
}


function load_tracer_tree_view() {
    $.get("tracers",
        function (data) {
            $.each(data, function (index, value) {
                add_tracer_run(value)
            });
            update_tracing_tree();
        })
        .error(function () {
            $('body').removeClass('waiting');
            document.body.innerHTML = "500 Error..";
        })
}


function drawChart(title, data) {
    const options = {
        title: title,
        legend: 'none',
        colors: ['#070794', '#e6693e', '#ec8f6e', '#f3b49f', '#f6c7b6'],
        backgroundColor: '#caece8',
        is3D: true

    };
    const div = document.createElement('div');
    div.setAttribute("class", "trace_chart");
    document.getElementById('right').appendChild(div);
    const chart = new google.visualization.LineChart(div);
    chart.draw(google.visualization.arrayToDataTable(data), options);
}

function download_csv(uuid) {
    // Downloads the tracing data for the passed in run.

    // http://localhost:6900/get_csv_name?uuid=1e7c356f-16b3-485c-a4f0-06872919285e

    $.get("get_csv_name?uuid=" + uuid, function (data) {
        const uri = "tracing_data_handler_as_csv?uuid=" + uuid;
        const link = document.createElement("a");
        link.download = data.csv_name;
        link.href = uri;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }).error(function () {
        $('body').removeClass('waiting');
        alert("500 Error..");
    });




}

function load_run_info(uuid) {
    $('body').addClass('waiting');

    $.get("tracing_data_handler?uuid=" + uuid, function (data) {
        $("#right").empty();

        for (const property in data) {
            drawChart(property, data[property])
        }

        $('body').removeClass('waiting');
    }).error(function () {
            $('body').removeClass('waiting');
            alert("500 Error..");
        });

    $.get("trace_run_info?uuid=" + uuid, function (data) {
        var txt = '<label>Started</label> <value>' + data['started'] + '</value><label>Count</label><value>'
            + data['counter'] + '</value><label>Duration</label><value>' + data['duration'] + '</value>';
        $("#tracer_run_name").html(data['app_name']);

        // Add the csv download button.
        txt += "<button id = 'download_csv_btn' style='margin-left:102px;'" +
            " >Download csv</button>";

        $("#tracer_description").html(txt);

        // In download button add the click event.
        $("#download_csv_btn").on("click", function () {
            download_csv(uuid);
        });
    }).error(function () {
        $('body').removeClass('waiting');
        alert("500 Error..");
    });
}