var debug=true;
var inputColNames={"PET":["Date", "Inflow-Mohembo", "Rainfall-Maun", "Rainfall-Shakawe", "PET-Maun"], "Temp":["Date", "Inflow", "Rainfall-Maun", "Rainfall-Shakawe", "MinTemp-Maun", "MaxTemp-Maun"]};
var serverparamFile;
var serverinputFile;
var serverinitcondFile;
var expID=Math.floor(Math.random()*100000000);
var resultsDir="uploads/";
var uploadsDir="uploads/";
var maxfileSize=1000000;
var maxts=1200;
var inputQC=false;
var modelRun=false;

var outputsList=JSON.parse('{"alloutflows": ["Outflows from all model units", "checked", "csv", "Mm3/month"], "allinundation":["Inundated area of all model units", "checked", "csv", "km2"], "totalinundation":["Total inundated area", "checked", "csv", "km2"], "totalecoregions":["Eco-hydrological regions for the entire system", "", "csv", "km2"], "animatedinundation": ["Animation of inundated area", "", "gif", "km2"]}');



function initialize () {
    txt="";
    txt+="<form id='expForm' method='post' enctype='multipart/form-data' action='upload.php' autocomplete='off'>";
    txt+="<div class=form-group>";
    txt+="<label for=sessionID>Experiment ID (automatically assigned):</label>";
    txt+="<input type=text class='form-control contained' id=expID value="+expID+" disabled hidden>";
    txt+="</div>";
    txt+="<div class=form-group>";
    txt+="<label for=expCode>Experiment code: </label>";
    txt+="<input type=text class='form-control contained' id=expCode value=test1>";
    txt+="</div>";
    txt+="<div class=form-group>";
    txt+="<label for=expDescription>Experiment description: </label>";
    txt+="<textarea class='form-control contained' rows=5 id=expDescription></textarea>";
    txt+="</div>";
    txt+="<div class=form-group>";
    txt+="<label for=userName>User name: </label>";
    txt+="<input class='form-control contained' id=userName>";
    txt+="</div>";
//    txt+="<input type=button class='btn btn-info' value='Load previous experiment'>";
    txt+="</form>";

    $("#experimentContainer").html(txt);


    txt="" 
    txt+="<form id='inputForm' method='post' enctype='multipart/form-data' action='upload.php' autocomplete='off'>";
    txt+="<div class='input-group'>";
    txt+="<input class='form-control fileName' type='text' id=inputFileName name=input>";
    txt+="<div class='input-group-btn'>";
    txt+="<label for='inputFileSelector' class='btn btn-primary'>Browse</label>";
    txt+="</div>";
    txt+="</div>";
    txt+="<input type='file' name='input' id='inputFileSelector' class='fileSelector' style='visibility:hidden'>";
    txt+="<div id=inputError></div>";
    txt+="<div class='hidden' id=inputFileInfo>";
    txt+="<p>Input file has <span id=nts></span> time steps, spanning the period of <span id=firstDate></span> to <span id=lastDate></span>";
    txt+="</div>";
    txt+="</form>";

    txt+="<div id=inputOutcome></div>";
    $("#inputContainer").html(txt);


    txt="";
    txt+="<form id='paramForm' method='post' enctype='multipart/form-data' action='upload.php' autocomplete='off'>";
    txt+=" <div class='radio'>";
    txt+="  <label><input type='radio' name='optparamFile' checked value=default>Use default</label>";
    txt+=" </div>";
    txt+=" <div class='radio'>";
    txt+="  <label><input type='radio' name='optparamFile' value=file>Load from file</label>";
    txt+=" </div>";
    txt+=" <div id=paramFileLoader>";
    txt+="  <div class='input-group'>";
    txt+="   <input class='form-control fileName' type='text' id=paramFileName name=param>";
    txt+="   <div class='input-group-btn'>";
    txt+="    <label for='paramFileSelector' class='btn btn-primary'>Browse</label>";
    txt+="   </div>";
    txt+="  </div>";
    txt+="  <input type='file' name='param' id='paramFileSelector' class='fileSelector actveInput' style='visibility:hidden'>";
    txt+=" </div>";
    txt+="</form>";
    txt+="<div id=paramError></div>";
    txt+="<div id=paramOutcome></div>";
    $("#paramContainer").html(txt);
    $("#paramFileLoader").hide();


    
    txt="";
    txt+="<form id='initcondForm' method='post' enctype='multipart/form-data' action='upload.php' autocomplete='off'>";
    txt+=" <div class='radio'>";
    txt+="  <label><input type='radio' name='optinitcondFile' value=default checked>Use default</label>";
    txt+=" </div>";
    txt+=" <div class='radio'>";
    txt+="  <label><input type='radio' name='optinitcondFile' value=file>Load from file</label>";
    txt+=" </div>";
    txt+=" <div id=initcondFileLoader>";
    txt+="<div class='input-group'>";
    txt+="<input class='form-control fileName' type='text' id=initcondFileName name=initcond>";
    txt+="<div class='input-group-btn'>";
    txt+="<label for='initcondFileSelector' class='btn btn-primary'>Browse</label>";
    txt+="</div>";
    txt+="</div>";
    txt+="<input type='file' name='initcond' id='initcondFileSelector' class='fileSelector' style='visibility:hidden'>";
    txt+="</div>";
    txt+="</form>";
    txt+="<div id=initcondError></div>";
    txt+="<div id=initcondOutcome></div>";
    $("#initcondContainer").html(txt);
    $("#initcondFileLoader").hide();
  
    txt="";
    txt+="<form id='optForm' method='post' enctype='multipart/form-data' action='upload.php' autocomplete='off'>";
    txt+="<div class=form-group>";
    txt+="<label for=spinup>Spin-up months (will be skipped from output, 0 for no spin-up):</label>";
    txt+="<input type=text class='form-control contained activeInput' id=spinup value=12>";
    txt+="</div>";
    txt+="<b>Model output</b>";
    txt+="<div class='input-group' id=outputs>";
    for (var key in outputsList){
        txt+="<div class=checkbox><label><input class=activeInput type=checkbox name=outputs[] value="+key+" id="+key+" "+outputsList[key][1]+">"+outputsList[key][0]+"</label></div>";
    }
    txt+="</div>";
    txt+="</form>";
    txt+="<div id=optOutcome></div>";
    $("#optContainer").html(txt);
    $("#optrunConfig").hide();

 
    txt="";
    txt+="<form id='runForm' method='post' enctype='multipart/form-data' action='upload.php' autocomplete='off'>";
    txt+="<div class='input-group'>";
    txt+="<input type=button class='btn btn-primary mx-1 my-1' id=checkinputButton value='Check required data' onClick=populatecheckRunData()>";
    txt+="</div>";
    txt+="<div id=runError></div>";
    txt+="<input type=button class='btn btn-primary mx-1 my-1 disabled' id=runmodelButton value='Run model' disabled>";
    txt+="</form>";
    txt+="<div id=runOutcome></div>";
    $("#runContainer").html(txt);



    txt="";
    txt+="<div id=resultsError><div>";
    txt+="<div id=resultsOutcome>Nothing to see here yet. Run the model first<div>";
    $("#resultsContainer").html(txt);
    if (debug){ 
        showModel(); //opens model tab
    }

    $('.fileName').on('click', function() {
        fileType=this.name;
        console.log(fileType);
        $('#'+fileType+'FileSelector').trigger('click');
    });


}


$(document).on('change','input[type=radio]', function(event){
    if (this.name=="optinitcondFile"){
        if (this.value=="file"){
            $("#initcondFileLoader").show();
        }else{
            $("#initcondFileLoader").hide();
        }
    }
    if (this.name=="optparamFile"){
        if (this.value=="file"){
            $("#paramFileLoader").show();
        }else{
            $("#paramFileLoader").hide();
        }
    }
});



$(document).on('change','.fileSelector', function(event){
    var file=event.target.files[0];
    if(event.target.files.length>0){
        fileType=event.target.name;
        errorDiv=fileType+"Error";
        //resetting fields
        $("#"+errorDiv).html("");
        $("#"+fileType+"Outcome").html("");
        $("#"+fileType+"FileName").val("");
        size=file.size;
        tmp=file.name.split(".");
        ext=tmp[tmp.length-1];
        if(size>maxfileSize){
            showfileloadError(fileType, "File size too large. Expected <"+maxfileSize+" Bytes, file "+file.name+" is "+size+ "Bytes large", true);
            $("#"+fileType+"FileSelector").val(null);
        }else if (ext!="csv"){
            showfileloadError(fileType, "Wrong file type (extension). Expected csv, file "+file.name+" has "+ext, true);
            $("#"+fileType+"FileSelector").val(null);
        }else{
            getAsText(file, fileType);
        }
        //reset error in run check, if any
        $("#runError").html("");
    }
});




function showfileloadError(fileType, message, iserror){
    if (iserror){
        alertType="alert-warning";
    }else{
        alertType="alert-success";
    }
    txt="<div class='alert "+alertType+" alert-dismissible'>";
    txt+="<a href='#' class='close' data-dismiss='alert' aria-label='close'>&times;</a>";
    txt+="<strong>"+message;
    txt+="</div>";
    $("#"+fileType+"Error").html(txt);
}





function getAsText(aFile, fileType) {
    targetDiv=fileType+"Outcome"
    var reader = new FileReader();
    // Read file into memory
    reader.readAsText(aFile);
    // Handle progress, success, and errors
    reader.onprogress = function(){
        $("#"+targetDiv).html('<img src="./static/img/ajax-loader.gif" alt="Uploading...." class=centered>');
    };
    reader.onload = function(evt){
        var fileString = evt.target.result;
        if(fileType=="input"){
            $("#inputFileName").val(aFile.name);
            showInput(fileString, aFile.name);
        }else if(fileType=="initcond"){
            $("#initcondFileName").val(aFile.name);
            showinitCond(fileString);
        }else if(fileType=="param"){
            $("#paramFileName").val(aFile.name);
            showParam(fileString);
        }
    };
    reader.onerror = function(){
        console.log("error");
        console.log(reader.error);
        showfileloadError(fileType, "error reading file:</br>"+reader.error);
    };
}




function showParam(rawdata){
    outcome=false;
    $("#paramOutcome").html(rawdata);
}



function showinitCond(rawdata){
    outcome=false;
}



function showInput(rawdata, filename){
    error=false;
    arraydata=parseCSV(rawdata);

    //QC of csv data;
    //checking number of columns
    ncol=arraydata[0].length;
    nts=arraydata.length-1; //because of header
    if (ncol==5){
        colnames=inputColNames['PET'];
    }else if(ncol==6){
        colnames=inputColNames['Temp'];
    }else{
        response="expected 5 or 6 columns in csv file, "+filename+" has "+ncol;
        error=true;
    }
    //checking if columns named as expected
    if (error==false){
        for(var c=0, len=ncol; c < len; c++){
            if(colnames[c]!=arraydata[0][c]){
                error=true;
                col=c+1;
                response="in column "+col+" expected "+colnames[c]+", "+filename+" has "+arraydata[0][c];
            }
        }
    }

    //checking time steps limit
    if (error==false){
        if(nts>maxts){
            error=true;
            response="there are "+nts+" time steps in "+filename+". Maximum allowed is"+maxts;
        }
    }

    //checking if values are numeric
    if (error==false){
        for(var r=1, lenr=nts; r <= lenr; r++){
            for(var c=1, lenc=ncol; c < lenc; c++){
                 curval=arraydata[r][c];
                 if(isNaN(curval) | curval==""){
                     error=true;
                     response="in row "+r+" column "+c+" of "+filename+" there is a non-numeric or empty value";
                 }
            }
        }
    }

    //checking if dates are OK
    if (error==false){
        for(var r=1, lenr=nts; r <= lenr; r++){
             curdate=new Date(arraydata[r][0]);
             if(isNaN(curdate)){
                 error=true;
                 response="in row "+r+" of "+filename+" there is a non valid date, "+arraydata[r][0];
             }
        }
    }


    if (error==true){
       //resetting
       $("#inputOutcome").html("");
       $("#inputFileName").val(null);
       $("#inputFileSelector").val(null);
       showfileloadError("input", response, true);
       //resetting run form
       $("#serverinputFile").val(null);
       $("#serverinitcondFile").val(null);
       $("#serverparamFile").val(null);
       $("#serverinputFileName").html("undefined");
       $("#serverinitcondFileName").html("undefined");
       $("#serverparamFileName").html("undefined");
       $("#firstDate").html("undefined");
       $("#lastDate").html("undefined");
       $("#nts").html("undefined");
       $("#runmodelButton").addClass("disabled");
       $('#inputFileInfo').addClass("hidden");

    }else{
       showfileloadError("input", "file read successfuly", false); 
        seriesData=[];
        allData=[];
        seriesNames=[];
        ncol=arraydata[0].length;
        nrow=arraydata.length;
        $("#nts").html(nrow-1);
        for(var c=1, len=ncol; c < len; c++){
          //get var names
            seriesNames.push(arraydata[0][c]);
            allData.push(new Array());
        }
        var dteoptions = { year: 'numeric', month: 'short'}
        for(var r=1, lenr=nrow; r < lenr; r++){
            dte=new Date(arraydata[r][0]);
            if (r==1){
                var firstDate=Intl.DateTimeFormat('en-GB', dteoptions).format(dte)
                $("#firstDate").html(firstDate);
            }
            if (r==nrow-1){
                var lastDate=Intl.DateTimeFormat('en-GB', dteoptions).format(dte)
                $("#lastDate").html(lastDate);
            }
            dte=dte.valueOf();
            for(var c=1, lenc=ncol; c < lenc; c++){
                allData[c-1].push([dte, parseFloat(arraydata[r][c])])
            }
        }
        for(var c=1, len=ncol; c < len; c++){
            seriesData.push({id: c, name: seriesNames[c-1], data: allData[c-1], showInLegend:true});
        }
        $('#inputFileInfo').removeClass("hidden");
        plotTimeSeries("inputOutcome", seriesData, "Input data", "Inflow: [Mm3/month] <br>others: [mm/month]");
    }
}




function populatecheckRunData(){
    expCode=$("#expCode").val();
    inputFile=$("#inputFileSelector").val();
    paramOpt=$('input[name="paramOption"]:checked').val();
    initcondOpt=$('input[name="initcondOption"]:checked').val();
    firstDate=$("#firstDate").val();
    lastDate=$("#lastDate").val();
    nts=$("#nts").val();
    error=false;
    message="";
    $("#runError").html("");

    //checking if input file is defined
    if (expCode==""){
        message="Experiment code missing";
        showfileloadError("run",message,true);
        error=true;
        return false;
    }

    if(inputFile==""){
        message="File with input data missing";
        showfileloadError("run",message,true);
        error=true;
        return false;
    }

    //checking if param file is defined
    if (paramOpt=="file"){
        paramFile=$("#paramFileSelector").val();
        if (paramFile==""){
            message="Parameters are to be read from file, but file with parameters not provided";
            showfileloadError("run",message,true);
            error=true;
            return false;
        }
    }

    //checking if initcondfile is defined
    if (initcondOpt=="file"){
        initcondFile=$("#initcondFileSelector").val();
        if (initcondFile==""){
            message="Initial conditions are to be read from file, but file with initial condition data not provided";
            showfileloadError("run",message,true);
            error=true;
            return false;
        }
    }



    //checking spinup value
    spinup=parseFloat($("#spinup").val());
    nts=parseFloat($("#nts").html());

    if (isNaN(spinup) || !isFinite(spinup) || spinup>nts){
        message="Value for spinup should be a numeric value between 0 and "+nts;
        showfileloadError("run",message,true);
        error=true;
        return false;
    }

    //checking inputs
    nboxes=$("input[name='outputs[]']:checked").length;
    if(nboxes==0){
        message="There should be some outputs selected";
        showfileloadError("run",message,true);
        error=true;
        return false;
    }

    // uploading files
    uploadallFiles().then(function(results){
        //console.log(results);
        for (i in results){
            data=results[i];
            //console.log(data);
            data=JSON.parse(data);
            uploaderror=data[0]['error'];
            response=data[0]['response'];
            fileType=data[0]['fileType'];
            if (uploaderror){
                error=true;
                showfileloadError("run", response, true);
                return false;
            }
            if(fileType=="input"){serverinputFile=response;}
            if(fileType=="param"){serverparamFile=response;}
            if(fileType=="initcond"){serverinitcondFile=response;}
        }


        showfileloadError("run", "All appears to be OK. You can run the model now.", false);
        $("#runmodelButton").removeClass("disabled").removeAttr('disabled')
        $("#runOutcome").show();
    });
}



function uploadFile(fileType){
    form=$("#"+fileType+"Form")[0];
    formdata=new FormData(form);
    expCode=$("#expCode").val();
    if($("#"+fileType+"FileSelector").val()==""){
        //
        var responsearray=[]
        var response={};
        response.error=false;
        response.response="default";
        response.fileType=fileType;
        responsearray.push(response);
        return (JSON.stringify(responsearray));
    }else{
        return $.ajax({
            url: "upload.php?expID="+expID+"&expCode="+expCode,
            method: "POST",
            data: formdata,
            processData: false,
            contentType: false
        });
    }
}



async function uploadallFiles(){
    var promises=[];
    promises.push(await uploadFile("input"));
    promises.push(await uploadFile("initcond"));
    promises.push(await uploadFile("param"));
    //await Promise.all(response)
    return promises;
}



$(document).on('click','#runmodelButton', function(event){
    $("#runOutcome").html("");
    form=$("#optForm")[0];
    formdata=new FormData(form);
    console.log(formdata);
    spinup=$("#spinup").val();
    var outputs="";
    $('#outputs input:checked').each(function() {
        outputs=outputs+","+$(this).attr('value');
    });
    console.log(outputs)
    $("#runOutcome").html('<img src="./img/ajax-loader.gif" alt="Calculating...." class=centered>');
    console.log(serverinputFile,serverinitcondFile,serverparamFile);
    $.ajax({
        url: "runmodel.php?expID="+expID+"&spinup="+spinup+"&input="+serverinputFile+"&initcond="+serverinitcondFile+"&param="+serverparamFile+"&outputs="+outputs,
        method: "POST",
        data: formdata,
        processData: false,
        contentType: false,
        success: function (data) {
        // success callback
            console.log(data);
            data=JSON.parse(data);
            outcome=data[0]['outcome'];
            response=data[0]['response'];
            if (outcome!="success"){
                $("#runOutcome").html(outcome);
            }else{
                txt="";
                for (line in response){
                txt+=response[line]+"<br>";
                }
                $("#runOutcome").html(txt);
                populateResults(expID);
                modelRun=true;
            }
        }
    });
});


function checkRunData(){
    runID=$("#runID").val();
    nboxes=$("input[name='outputs[]']:checked").length;
    isInt=Number.isInteger(parseInt($("#spinup").val()));
    nts=$("#nts").val();
    if(isInt){
        isLow=parseInt($("#spinup").val())<parseInt(nts);
    }else{
        isLow=false;
    }
    if(runID!="" && nboxes>0 && isInt && isLow){
        outcome=true;
    }else{
        outcome=false;
    }
    return outcome;
}




function populateResults(runID){
    txt="<h4>Available outputs</h4>";
    files=$("input[name='outputs[]']:checked");
    nfiles=files.length;
    for(var c=0, len=nfiles; c < len; c++){
        fileCode=files[c].value;
        key=fileCode.split(".")[0];
        ext=outputsList[key][2];
        resultsFile=resultsDir+"/"+expID+"/"+expID+"-"+key+"."+ext;
        txt+="<b>"+outputsList[key][0]+": </b><label> plot <input type=checkbox class=previewResults name=res-"+key+" id=res-"+key+" value="+resultsFile+"></label>";
        txt+=" or download output file: <a href="+resultsFile+">"+expID+"-"+key+"."+ext+"</a><br>";
        txt+="<div id=resultsOutcome-"+key+" class=outcome></div>";
    }
 
    $("#resultsContainer").html(txt);
    $("#showhide-results").html("[close]");
    $("#resultsContainer").show();
}




$(document).on('change','.previewResults', function(event){
    resID=$(this).attr("id");
    resID=resID.split("-")[1];
    resultFile=$(this).attr("value");
    if ($(this).is(':checked')==false){
        $("#resultsOutcome-"+resID).html("");
    }else{
        ext=resultFile.substring(resultFile.length - 3, resultFile.length);
        console.log(ext);
        if(ext=="csv"){
            readFile(resultFile, function(rawdata){
                arraydata=parseCSV(rawdata);
                seriesData=[];
                allData=[];
                seriesNames=[];
                ncol=arraydata[0].length;
                nrow=arraydata.length;
                for(var c=1, len=ncol; c < len; c++){
                  //get var names
                    seriesNames.push(arraydata[0][c]);
                    allData.push(new Array());
                }
                for(var r=1, lenr=nrow; r < lenr; r++){
                    dte=new Date(arraydata[r][0]);
                    if (r==1){firstDate=dte;}
                    if (r==nrow-1){lastDate=dte;}
                    dte=dte.valueOf();
                    for(var c=1, lenc=ncol; c < lenc; c++){
                        allData[c-1].push([dte, parseFloat(arraydata[r][c])])
                    }
                }
                for(var c=1, len=ncol; c < len; c++){
                    seriesData.push({id: c, name: seriesNames[c-1], data: allData[c-1], showInLegend:true});
                }
                console.log(resID);

                label=outputsList[resID][0]+"<br>"+outputsList[resID][3];
                outcome=plotTimeSeries("resultsOutcome-"+resID, seriesData, "Model results", label);
                if (outcome != true){
                   $("#resultsOutcome-"+resID).html("<span class=alert>"+response+"</span>");
                };
            });
        }else{
                   $("#resultsOutcome-"+resID).html("<img src="+resultFile+">");
        }
    }
});



$(document).on('click','.activeInput', function(event){
    if (modelRun){
        var retVal = confirm("Changing this will reset model output. Do you want to continue ?");
        if( retVal == true ) {
            $("#results_container").html("");
            $("#run_outcome").html("");
            modelRun=false;
            return true;
        }else{
            return false;
        }
    }

});


function readFile(_file, callback){
    $.get(_file,function(data){
        callback(data);
    });
}


function parseCSV(str) {
    //from https://stackoverflow.com/questions/1293147/javascript-code-to-parse-csv-data
    var arr = [];
    var quote = false;  // true means we're inside a quoted field

    // iterate over each character, keep track of current row and column (of the returned array)
    for (var row = 0, col = 0, c = 0; c < str.length; c++) {
        var cc = str[c], nc = str[c+1];        // current character, next character
        arr[row] = arr[row] || [];             // create a new row if necessary
        arr[row][col] = arr[row][col] || '';   // create a new column (start with empty string) if necessary

        // If the current character is a quotation mark, and we're inside a
        // quoted field, and the next character is also a quotation mark,
        // add a quotation mark to the current column and skip the next character
        if (cc == '"' && quote && nc == '"') { arr[row][col] += cc; ++c; continue; }  

        // If it's just one quotation mark, begin/end quoted field
        if (cc == '"') { quote = !quote; continue; }

        // If it's a comma and we're not in a quoted field, move on to the next column
        if (cc == ',' && !quote) { ++col; continue; }

        // If it's a newline (CRLF) and we're not in a quoted field, skip the next character
        // and move on to the next row and move to column 0 of that new row
        if (cc == '\r' && nc == '\n' && !quote) { ++row; col = 0; ++c; continue; }

        // If it's a newline (LF or CR) and we're not in a quoted field,
        // move on to the next row and move to column 0 of that new row
        if (cc == '\n' && !quote) { ++row; col = 0; continue; }
        if (cc == '\r' && !quote) { ++row; col = 0; continue; }

        // Otherwise, append the current character to the current column
        arr[row][col] += cc;
    }
    return arr;
}

function showHome(){
    $("#docsContents").hide()
    $("#modelContents").hide()
    $("#homeContents").show()
}

function showDocs(){
    $("#docsContents").show()
    $("#modelContents").hide()
    $("#homeContents").hide()
}

function showModel(){
    $("#docsContents").hide()
    $("#modelContents").show()
    $("#homeContents").hide()
}

function pageinModal(page,title){ 
    $.get(page, function(data){
        $(".modal-title").html(title);
        $(".modal-body").html(data);
        $('#myModal').modal('show');
    });
}

function textinModal(txt,title){ 
    $(".modal-title").html(title);
    $(".modal-body").html(txt);
    $('#myModal').modal('show');
}

function listsavedExp(){
    txt="<div>";
    txt+="<a>User run ID: <input type=text name=runID id=runID class=activeInput>";
    txt+="</div>";
    $("#selectexpDiv").html(txt).show();
}


