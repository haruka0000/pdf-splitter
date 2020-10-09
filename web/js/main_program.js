
var pdf_path = "";
var table = document.getElementById('maintable');

// SUBMITされたとき
async function get_file() {
    // ファイル入力
    pdf_path = await eel.get_file_path()();
    pdf_path_disp = document.getElementById("pdf-path-disp");
    pdf_path_disp.textContent = pdf_path;
    if (pdf_path != ""){
        document.getElementById("clear-btn").disabled = false;
        document.getElementById("default-btn").disabled = false;
        document.getElementById("commit-btn").disabled = false;
        // 再描画
        init_data();
    }
}

// SUBMITされたとき
async function get_folder() {
    // ファイル入力
    output_path = await eel.get_dir_path()();
    output_path_disp = document.getElementById("output-path-disp");
    if (output_path != ""){
        document.getElementById("submit-btn").disabled = false;
    } 
    output_path_disp.textContent = output_path;
}


async function init_data() {
    await eel.init_data();
    if (pdf_path != ""){
        let data = await eel.get_data()();
        set_data(data);
    }
}

async function update_table(){
    var table_d = get_table_inputs();
    var prefix = document.getElementById('prefix').value;
    await eel.update_data(table_d);
    await eel.set_prefix(prefix);
    let data = await eel.get_data()();
    set_data(data);
}


async function get_org_data() {
    await eel.set_org_data();
    let data = await eel.get_data()();
    set_data(data);
}

async function clear_data(){
    await eel.clear_data();
    let data = await eel.get_data()();
    set_data(data);
}

eel.expose(update_progressbar)
function update_progressbar(value, str_value){
    var p_bar = document.getElementById('split-progress');
    p_bar.value = value;
    p_bar.textContent = str_value;
}

function set_data(data){
    var empty_rows_num = 5;
    if (data.length === 1){ empty_rows_num = 10; }
    for (var i = 0; i < empty_rows_num; i++) {
        data.push(["", "" ,""])
    }
    table.innerHTML = ''
    var thead = document.createElement('thead');
    var tbody = document.createElement('tbody');
    table.appendChild(thead);
    table.appendChild(tbody);
    // tr部分のループ
    for (var i = 0; i < data.length; i++) {
        // tr要素を生成
        var tr = document.createElement('tr');
        tr.name = "table_row"
        // th・td部分のループ
        for (var j = 0; j < data[i].length+1; j++) {
            // 1行目のtr要素の時
            if(i === 0) {
                var th = document.createElement('th');
                if (j == 0){
                    th.textContent = "";
                    th.style = "width: 30px; text-align: center;"
                } else{
                    th.textContent = data[i][j-1];
                    if (j == 1){ th.classList.add('text-cell'); }else{ th.classList.add('number-cell'); }
                }
                tr.appendChild(th)
            } else{
                var td = document.createElement('td');
                if (j === 0){
                    td.textContent = i;
                    td.style = "width: 30px; font-size: 24; text-align: center;"
                } else{
                    var cell = document.createElement('input');
                    cell.classList.add('cellinputs', 'search-input');
                    if (j == 1){
                        cell.classList.add('text-cell');
                        td.classList.add('text-cell');
                    } else{
                        cell.classList.add('number-cell');
                        cell.type = "number"
                        td.classList.add('number-cell');
                    }
                    cell.name = "table_cell"
                    if (data[i][j] != ""){
                        cell.value = data[i][j-1];
                    }
                    td.appendChild(cell)
                }
                tr.appendChild(td) 
            }
        }
        // 1行目のtr要素の時
        if(i === 0) {
            thead.appendChild(tr);
        } else{
            tbody.appendChild(tr);
        }
    }
}



function get_table_inputs(){
    var table = document.getElementById('maintable');
    var t_rows = table.getElementsByTagName('tr');
    var t_arr = [];
    // th の取得
    var th_row = t_rows[0].getElementsByTagName("th");
    var r_arr = [];
    for (var i = 1; i < th_row.length; i++) {
        r_arr.push(th_row[i].textContent);
    }
    t_arr.push(r_arr);
    // td の取得
    for (var i = 1; i < t_rows.length; i++) {
        var r_arr = [];
        var cells = t_rows[i].getElementsByTagName("input")
        for (var j = 0; j < cells.length; j++) {
            r_arr.push(cells[j].value);
        }
        t_arr.push(r_arr);
    }
    return t_arr
}

async function split_pdf(){
    await eel.split_pdf();
}