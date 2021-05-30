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

function load_run_info(uuid) {
    $('body').addClass('waiting');

    $.get("tracer_run?uuid=" + uuid, function (data) {
        $("#right").empty()
        $("#right").append(data)
        $('body').removeClass('waiting');
    })
    .error(function () {
            $('body').removeClass('waiting');
            alert("500 Error..");
        });

    $.get("trace_run_info?uuid=" + uuid, function (data) {
        var txt = '<label>Started</label> <value>' + data['started'] + '</value><label>Count</label><value>'
            + data['counter'] + '</value><label>Duration</label><value>' + data['duration'] +'</value>';
        $("#tracer_run_name").html(data['app_name']);
        $("#tracer_description").html(txt);
    }).error(function () {
            $('body').removeClass('waiting');
            alert("500 Error..");
        });
}