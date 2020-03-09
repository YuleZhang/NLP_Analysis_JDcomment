//读取CSV文件
    function readCsv(){
            var files = document.getElementById("file").files;
            var reg = new RegExp(".*,\".*,.*\"$");
            var tableObj=document.getElementById('tbTop10');//根据id获得表格元素
            //if(tableObj.rows.length>1){return;}
            clearTB();
            if(files.length) {
                var file = files[0];
                var reader = new FileReader();
                if(typeof FileReader == 'undefined') {
                    layer.alert("你的浏览器不支持FileReader接口！", {title: "提示", skin: "layui-layer-molv"});
                }
                reader.readAsText(file);
                reader.onload = function(val) {
                    var relArr = this.result.split("\n");
                    relArr = com_sort(relArr);
                    if(!$.isEmptyObject(relArr) && relArr.length > 1) {
                        csvData = String(relArr);
                        for(var key = 1, len = relArr.length; key < 11; key++) {
                            goodName = csvData.split(",")[2+5*key];
                            price = csvData.split(",")[1+5*key];
                            sales = csvData.split(",")[3+5*key];
                            score = csvData.split(",")[4+5*key];
                            addRow(key,goodName,price,sales,score);
                        }
                }
            }
        }
        else{
            alert("请先选择文件");
        }
    };
    //添加一行
    function addRow(seq,goodName,price,sales,score){ 
            var result="";
            result +="<tr>";
            result +="<td style='text-align: center;'>"+seq+"</td>";
            result +="<td style='text-align: center;'>"+goodName+"</td>";
            result +="<td style='text-align: center;'>"+price+"</td>";
            result +="<td style='text-align: center;'>"+sales+"</td>";
            result +="<td style='text-align: center;'>"+score+"</td>";
            result +="</tr>";
            $("#tbTop10 tbody").append(result);
        };
    function freshDefault(){
        // document.getElementById("file").addEventListener("change",function () {
                
  //      });
        var files = document.getElementById("file").files;
        var file;
        if(files.length) {
            file = files[0];
        }
        var input = document.getElementById("curFile");
        input.setAttribute("placeholder", String(file.name));
        input.setAttribute('class', 'form-control');
        console.log("changessss");
    }
    //清空table
    function clearTB(){ 
        tableObj = document.getElementById("tbTop10");
        rowcount = tableObj.rows.length;
        for(i=rowcount  - 1;i > 0; i--){
           tableObj.deleteRow(i);
        }
    };
    //csv数据排序
    function com_sort(arr){
        arr = arr.filter(item => item);
        lenArr = arr.length;
        var price_arr_norm = new Array();
        var sales_arr_norm = new Array();
        var score_arr_norm = new Array();
        for(i=0;i<lenArr;i++){
            price = arr[i].split(",")[1];
            sales = arr[i].split(",")[3];
            score = arr[i].split(",")[4];
            if(price!=undefined){
                price_arr_norm[i] = price;
            }
            if(sales!=undefined){
                sales_arr_norm[i] = sales;
            }
            if(score!=undefined){
                score_arr_norm[i] = score;
            }
        }
        //console.log(price_arr);
        var max_price = getMaxV(price_arr_norm);
        var min_price = getMinV(price_arr_norm);
        var max_sales = getMaxV(sales_arr_norm);
        var min_sales = getMinV(sales_arr_norm);
        var max_score = getMaxV(score_arr_norm);
        var min_score = getMinV(score_arr_norm);
        for(i=0;i<arr.length;i++){
            price_arr_norm[i] = normalization(price_arr_norm[i],max_price,min_price);
            sales_arr_norm[i] = normalization(sales_arr_norm[i],max_sales,min_sales);
            score_arr_norm[i] = normalization(score_arr_norm[i],max_score,min_score)
        }
        var price_val = $('#priceSelect option:selected').text();//选中的文本
        var sales_val = $('#salesSelect option:selected').text();
        var score_val = $('#commentSelect option:selected').text();
        var price_weight = 0;
        var sales_weight = 0;
        var score_weight = 0;
        switch(price_val){
            case "越贵越好！":price_weight=3;break;
            case "可以接受一般水平":price_weight=2;break;
            case "我要便宜货！":price_weight=1;break;
            default:break;
        }
        switch(sales_val){

            case "我一定要跟紧潮流":sales_weight=3;break;
            case "无所谓":sales_weight=1;break;
            default:break;
        }
        switch(score_val){
            case "评价最重要":score_weight=3;break;
            case "一般般但要考虑":score_weight=2;break;
            case "I dont't care!!!":score_weight=1;break;
            default:break;
        }
        var sum_score = new Array();
        for(i=0;i<arr.length;i++){
            sum_score[i]=price_weight*price_arr_norm[i] + sales_weight*sales_arr_norm[i]+score_weight*score_arr_norm[i];
        }
        console.log(sum_score);
        //选择排序
        var min,loc;
        for(i=0;i<sum_score.length-1;i++){
            loc = i;
            for(j=i+1;j<sum_score.length;j++){
                if(parseFloat(sum_score[loc])<parseFloat(sum_score[j])){
                    loc = j;
                }
            }
            //交换位置
            var tmpVal = sum_score[i];
            var tmpList = arr[i];
            sum_score[i] = sum_score[loc];
            sum_score[loc] = tmpVal;
            arr[i] = arr[loc];
            arr[loc] = tmpList;
        }
        console.log(sum_score);
        return arr;
    };
    // 获取最大值
    function getMaxV(arr) {
      let max = 0
      for (let item of arr) {
        if (max < Number(item))
          max = Number(item);
      }
      return max
    }
     
    // 获取最小值
    function getMinV(arr) {
      let min = 1000000
      for (let item of arr) {
        if (min > Number(item))
          min = Number(item);
      }
      return min
    }
     
    // 归一化处理
    function normalization(arri, max, min) {
      let normalizationRatio = (arri - min) / (max - min)
      return normalizationRatio
    }