var debug=true;
var inputColNames={"PET":["Date", "Inflow-Mohembo", "Rainfall-Maun", "Rainfall-Shakawe", "PET-Maun"], "Temp":["Date", "Inflow", "Rainfall-Maun", "Rainfall-Shakawe", "MinTemp-Maun", "MaxTemp-Maun"]};
var serverparamFile;
var serverinputFile;
var serverinitcondFile;
var expID=Math.floor(Math.random()*100000000);
var resultsDir="public/";
var uploadsDir="public/";
var maxfileSize=1000000;
var maxts=600;
var inputQC=false;
var modelRun=false;
var modelChecked=false;
var modelUnits=15
var modelsubUnits=10

var outputsList=JSON.parse('{"alloutflows": ["Outflows from all model units", "checked", "csv", "Mm3/month","timeseries"],\
"allinundation":["Inundated area of all model units", "checked", "csv", "km2","timeseries"],\
"totalinundation":["Total inundated area", "checked", "csv", "km2","timeseries"],\
"allvolumes":["storages of all model units", "checked", "csv", "Mm3","timeseries"],\
"totalecoregions":["Eco-hydrological regions for the entire system", "", "csv", "km2","timeseries"],\
"allecoregions":["Eco-hydrological regions for each of model units", "", "csv", "km2","timeseries"],\
"animatedinundation": ["Animation of inundated area", "", "gif", "km2","none"],\
"finalcond": ["Final storages in all units (to be used as initial condition for a different run)", "", "csv", "various","none"]}');



function initialize () {
    txt="";
    txt+="<form id='expForm' method='post' enctype='multipart/form-data' action='upload.php' autocomplete='off'>";
    txt+="<div class=form-group>";
    txt+="<label for=sessionID>Experiment ID (automatically assigned):</label><a href='#' class=help data-pload='expID_help'>?</a>";
    txt+="<input type=text class='form-control contained' id=expID value="+expID+" disabled hidden>";
    txt+="</div>";
    txt+="<div class=form-group>";
    txt+="<label for=expCode>Experiment code: </label><a href='#' class=help data-pload='expCode_help'>?</a>";
    txt+="<input type=text class='form-control contained activeInput' id=expCode value=test1>";
    txt+="</div>";
//    txt+="<div class=form-group>";
//    txt+="<label for=expDescription>Experiment description: </label>";
//    txt+="<textarea class='form-control contained' rows=5 id=expDescription></textarea>";
//    txt+="</div>";
//    txt+="<div class=form-group>";
//    txt+="<label for=userName>User name: </label>";
//    txt+="<input class='form-control contained' id=userName>";
//    txt+="</div>";
//    txt+="<input type=button class='btn btn-info' value='Load previous experiment'>";
    txt+="</form>";

    $("#experimentContainer").html(txt);


    txt="" 
    txt+="<form id='inputForm' method='post' enctype='multipart/form-data' action='upload.php' autocomplete='off'>";
    txt+="<label>Input data file:</label><a href='#' class=help data-pload='inputFile_help'>?</a>";
    txt+="<div class='input-group'>";
    txt+="<input class='form-control fileName activeInput' type='text' id=inputFileName name=input>";
    txt+="<div class='input-group-btn'>";
    txt+="<label for='inputFileSelector' class='btn btn-primary activeInput'>Browse</label>";
    txt+="</div>";
    txt+="</div>";
    txt+="<input type='file' name='input' id='inputFileSelector' class='fileSelector activeInput' style='visibility:hidden'>";
    txt+="<div id=inputAlert></div>";
    txt+="<div class='hidden' id=inputFileInfo>";
    txt+="<p>Input file has <span id=nts></span> time steps, spanning the period of <span id=firstDate></span> to <span id=lastDate></span>";
    txt+="</div>";
    txt+="</form>";

    txt+="<div id=inputOutcome></div>";
    $("#inputContainer").html(txt);


    txt="";
    txt+="<form id='paramForm' method='post' enctype='multipart/form-data' action='upload.php' autocomplete='off'>";
    txt+="<label>Model parameters:</label><a href='#' class=help data-pload='paramFile_help'>?</a>";
    txt+=" <div class='radio'>";
    txt+="  <label><input class=activeInput type='radio' name='paramFileOpt' checked value=default>Use default</label>";
    txt+=" </div>";
    txt+=" <div class='radio'>";
    txt+="  <label><input class=activeInput type='radio' name='paramFileOpt' value=file>Load from file</label>";
    txt+=" </div>";
    txt+=" <div id=paramFileLoader>";
    txt+="  <div class='input-group'>";
    txt+="   <input class='form-control fileName' type='text' id=paramFileName name=param>";
    txt+="   <div class='input-group-btn'>";
    txt+="    <label for='paramFileSelector' class='btn btn-primary'>Browse</label>";
    txt+="   </div>";
    txt+="  </div>";
    txt+="  <input type='file' name='param' id='paramFileSelector' class='fileSelector activeInput' style='visibility:hidden'>";
    txt+=" </div>";
    txt+="</form>";
    txt+="<div id=paramAlert></div>";
    txt+="<div id=paramOutcome></div>";
    $("#paramContainer").html(txt);
    $("#paramFileLoader").hide();


    
    txt="";
    txt+="<form id='initcondForm' method='post' enctype='multipart/form-data' action='upload.php' autocomplete='off'>";
    txt+="<label>Model initial conditions:</label><a href='#' class=help data-pload='initcondFile_help'>?</a>";
    txt+=" <div class='radio'>";
    txt+="  <label><input class=activeInput type='radio' name='initcondFileOpt' value=default checked>Use default</label>";
    txt+=" </div>";
    txt+=" <div class='radio'>";
    txt+="  <label><input class=activeInput type='radio' name='initcondFileOpt' value=file>Load from file</label>";
    txt+=" </div>";
    txt+=" <div id=initcondFileLoader>";
    txt+="<div class='input-group'>";
    txt+="<input class='form-control fileName activeInput' type='text' id=initcondFileName name=initcond>";
    txt+="<div class='input-group-btn'>";
    txt+="<label for='initcondFileSelector' class='btn btn-primary activeInput'>Browse</label>";
    txt+="</div>";
    txt+="</div>";
    txt+="<input type='file' name='initcond' id='initcondFileSelector' class='fileSelector' style='visibility:hidden'>";
    txt+="</div>";
    txt+="</form>";
    txt+="<div id=initcondAlert></div>";
    txt+="<div id=initcondOutcome></div>";
    $("#initcondContainer").html(txt);
    $("#initcondFileLoader").hide();
  
    txt="";
    txt+="<form id='optForm' method='post' enctype='multipart/form-data' action='#' autocomplete='off'>";
    txt+="<div class=form-group>";
    txt+="<label for=spinup>Spin-up years (0 for no spin-up, not more than 5): <a href='#' class=help data-pload='spinup_help'>?</a></label>";
    txt+="<input type=text class='form-control contained activeInput' id=spinup value=5>";
    txt+="</div>";
    txt+="<label>Model output</label><a href='#' class=help data-pload='modeloutput_help'>?</a>";
    txt+="<div class='input-group' id=outputs>";
    for (var key in outputsList){
        txt+="<div class=checkbox><label><input class=activeInput type=checkbox name=outputs[] value="+key+" id="+key+" "+outputsList[key][1]+">"+outputsList[key][0]+"</label><a href='#' class=help data-pload='"+key+"_help'>?</a></div>";
    }
    txt+="</div>";
    txt+="</form>";
    txt+="<div id=optOutcome></div>";
    $("#optContainer").html(txt);
    $("#optrunConfig").hide();

 
    txt="";
    txt+="<form id='runForm' method='post' enctype='multipart/form-data' action='upload.php' autocomplete='off'>";
    txt+="<div class='input-group'>";
    txt+="<input type=button class='btn btn-primary mx-1 my-1' id=checkrunButton value='Validate simulation inputs'>";
    txt+="<input type=button class='btn btn-primary mx-1 my-1 disabled' id=runmodelButton value='Run model' disabled>";
    txt+="<a href='#' class=help data-pload='runbuttons_help'>?</a></div>";
    txt+="</form>";
    txt+="<div id=runAlert></div>";
    txt+="<div id=runOutcome></div>";
    $("#runContainer").html(txt);

    txt="";
    txt+="<div id=resultsAlert></div>";
    txt+="<div id=resultsOutcome>Nothing to see here yet. Run the model first</div>";
    $("#resultsContainer").html(txt);

    if (debug){ 
        showModel(); //opens model tab
    }
}


// switching between default and file source of parameters and initial conditions
$(document).on('change','input[type=radio]', function(event){
    if (this.name=="initcondFileOpt"){
        if (this.value=="file"){
            $("#initcondFileLoader").show();
        }else{
            $("#initcondFileLoader").hide();
            $("#initcondFileName").val("");
            $("#initcondFileSelector").val("");
            $("#initcondAlert").html("");
            $("#initcondOutcome").html("");
        }
    }
    if (this.name=="paramFileOpt"){
        if (this.value=="file"){
            $("#paramFileLoader").show();
        }else{
            $("#paramFileLoader").hide();
            $("#paramFileName").val("");
            $("#paramFileSelector").val("");
            $("#paramAlert").html("");
            $("#paramOutcome").html("");
        }
    }
});


//binding exposed file input field to the proper but hidden file selector element
$(document).on('click','.fileName', function(event){
    fileType=this.name;
    console.log(fileType);
    $('#'+fileType+'FileSelector').trigger('click');
});


// file loading event
$(document).on('change','.fileSelector', function(event){
    //console.log("checking");
    var file=event.target.files[0];
    if(event.target.files.length>0){
        fileType=event.target.name;
        //resetting fields
        $("#"+fileType+"Alert").html("");
        $("#"+fileType+"Outcome").html("");
        $("#"+fileType+"FileName").val("");
        size=file.size;
        tmp=file.name.split(".");
        ext=tmp[tmp.length-1];
        if(size>maxfileSize){
            showAlert(fileType, "File size too large. Expected <"+maxfileSize+" Bytes, file "+file.name+" is "+size+ "Bytes large", "danger");
            $("#"+fileType+"FileSelector").val(null);
            return false
        }
        if (ext!="csv"){
            showAlert(fileType, "Wrong file type (extension). Expected csv, file "+file.name+" has "+ext, "danger");
            $("#"+fileType+"FileSelector").val(null);
            return false
        }
        // reading file
        getAsText(file, fileType);
        //reset error in run check, if any
        $("#runAlert").html("");
    }
});




function showAlert(alertField, message, alertType){
    txt="<div class='alert alert-"+alertType+" alert-dismissible'>";
    if (alertType=="danger"){
        alertType="Error";
    }
    txt+="<a href='#' class='close' data-dismiss='alert' aria-label='close'>&times;</a>";
    txt+="<strong>"+alertType+": "+message;
    txt+="</div>";
    $("#"+alertField+"Alert").html(txt);
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
            parseInput(fileString, aFile.name);
        }else if(fileType=="initcond"){
            $("#initcondFileName").val(aFile.name);
            parseinitCond(fileString);
        }else if(fileType=="param"){
            $("#paramFileName").val(aFile.name);
            parseParam(fileString);
        }
    };
    reader.onerror = function(){
        console.log("error");
        console.log(reader.error);
        showAlert(fileType, "error reading file:</br>"+reader.error, "danger");
    };
}




function parseParam(rawdata){
    arraydata=parseCSV(rawdata);
    //console.log(arraydata.length)
    //checking if values numeric and in numbers corresponding to expectations
    nrows=arraydata.length
    for(var r=0, lenr=nrows; r < lenr; r++){
        rowdata=arraydata[r];
        ncol=rowdata.length;
        nvals=0
        for(var c=0, lenc=ncol; c < lenc; c++){
            curval=rowdata[c];
            //console.log(curval);
            if(curval===""){
                if (nvals>=2){
                    //allwell
                }else{
                    message="in row "+(r+1)+" column "+(c+1)+" there is empty value";
                    showAlert("param",message,"danger");
                    $("#paramOutcome").html("");
                    return false
                }
            }else{
                nvals=nvals+1
                if (c>0){
                    curval=parseFloat(rowdata[c]);
                    //console.log("nonempty ", curval);
                    if(isNaN(curval)){
                        message="in row "+(r+1)+" column "+(c+1)+" there is a non-numeric entry";
                        showAlert("param",message,"danger");
                        $("#paramOutcome").html("");
                        return false
                    }
                }
            }
        }
    }

    message="File appears to be correct";
    showAlert("param",message,"success");
 
    txt="";
    for(var r=0, lenr=arraydata.length; r < lenr; r++){
        rowdata=arraydata[r];
        txt+=rowdata+"</br>";
    }
    panelTxt=generatePanel(txt,"paramPanel", false, "Preview file contents")
    $("#paramOutcome").html(panelTxt);
}



function parseinitCond(rawdata){
    arraydata=parseCSV(rawdata);
    //console.log(arraydata.length)

    //checking number of rows
    nrow=arraydata.length;
    if (nrow!=modelUnits*3){
        message="expected "+modelUnits+" rows in csv file, this one has "+nrow;
        error=true;
        showAlert("initcond",message,"danger");
        $("#initcondOutcome").html("");
        return false
    }

    //checking if values numeric and in numbers corresponding to expectations
    for(var r=0, lenr=modelUnits*3; r < lenr; r++){
        rowdata=arraydata[r];
        ncol=rowdata.length;
        if (r<modelUnits){
            expCol=2;
        }else{
            expCol=(modelsubUnits+1);
        }
        nvals=1
        for(var c=1, lenc=ncol; c < lenc; c++){
            curval=rowdata[c];
            //console.log(curval);
            if(curval===""){
                if (nvals>=expCol){
                    //allwell
                }else{
                    //console.log(nvals,expCol);
                    message="in row "+(r+1)+" column "+(c+1)+" there is empty value";
                    showAlert("initcond",message,"danger");
                    $("#initcondOutcome").html("");
                    return false
                }
            }else{
                nvals=nvals+1
                curval=parseFloat(rowdata[c]);
                //console.log("nonempty ", curval);
                if(isNaN(curval)){
                    error=true;
                    message="in row "+(r+1)+" column "+(c+1)+" there is a non-numeric entry";
                    showAlert("initcond",message,"danger");
                    $("#initcondOutcome").html("");
                    return false
                }
            }
        }
        if(nvals!=expCol){
            //console.log("ncol");
            message="in row "+(r+1)+" there are "+nvals+" values. Expected "+expCol;
            showAlert("initcond",message,"danger");
            $("#initcondOutcome").html("");
            return false
        }
    }

    message="File appears to be correct";
    showAlert("initcond",message,"success");
    txt="";
    for(var r=0, lenr=modelUnits*3; r < lenr; r++){
        rowdata=arraydata[r];
        txt+=rowdata+"</br>";
    }

    panelTxt=generatePanel(txt,"initcondPanel", false, "Preview file contents")
    $("#initcondOutcome").html(panelTxt);
}



function parseInput(rawdata, filename){
    arraydata=parseCSV(rawdata);

    //QC of csv data;
    //checking number of columns
    ncol=arraydata[0].length;
    nts=arraydata.length-1; //because of header

//    $("#inputOutcome").html("");
//    $("#inputFileName").val(null);
//    $("#inputFileSelector").val(null);
    //resetting run form
    $("#firstDate").html("undefined");
    $("#lastDate").html("undefined");
    $("#nts").html("undefined");
    $("#runmodelButton").addClass("disabled");
    $('#inputFileInfo').addClass("hidden");


    if (ncol==5){
        colnames=inputColNames['PET'];
    }else if(ncol==6){
        colnames=inputColNames['Temp'];
    }else{
        message="expected 5 or 6 columns in csv file, "+filename+" has "+ncol;
        showAlert("input", message, "danger");
        return false;
    }

    //checking if columns named as expected
    for(var c=0, len=ncol; c < len; c++){
        if(colnames[c]!=arraydata[0][c]){
            col=c+1;
            message="in column "+col+" expected "+colnames[c]+", "+filename+" has "+arraydata[0][c];
            showAlert("input", message, "danger");
            return false;
        }
    }

    //checking time steps limit
    if(nts>maxts){
        message="there are "+nts+" time steps in "+filename+". Maximum allowed is"+maxts;
        showAlert("input", message, "danger");
        return false;
    }

    //checking if values are numeric
    for(var r=1, lenr=nts; r <= lenr; r++){
        for(var c=1, lenc=ncol; c < lenc; c++){
            curval=arraydata[r][c];
            if(isNaN(curval) | curval==""){
                message="in row "+r+" column "+c+" of "+filename+" there is a non-numeric or empty value";
                showAlert("input", message, "danger");
                return false;
            }
        }
    }

    //checking if dates are OK
    for(var r=1, lenr=nts; r <= lenr; r++){
         curdate=new Date(arraydata[r][0]);
         if(isNaN(curdate)){
            message="in row "+r+" of "+filename+" there is a non valid date, "+arraydata[r][0];
            showAlert("input", message, "danger");
            return false;
         }
    }

    //success
    showAlert("input", "file read successfuly", "success"); 

    //converting data to highcharts format
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

    txt="";
    for(var r=0, lenr=arraydata.length; r < lenr; r++){
        rowdata=arraydata[r];
        txt+=rowdata+"</br>";
    }
    txt=generatePanel(txt,"inputPanel", false, "Preview file contents")
    txt="<div id=inputOutcome-graph></div>"+txt;

    $("#inputOutcome").html(txt);


    plotTimeSeries("inputOutcome-graph", seriesData, "Input data", "Inflow: [Mm3/month] <br>others: [mm/month]");
}




// checking all data required to run model
$(document).on('click','#checkrunButton', function(event){
    $("#runAlert").html("");

    //checking experiment code
    expCode=$("#expCode").val();
    if (expCode==""){
        message="Experiment code missing";
        showAlert("run",message,"danger");
        return false;
    }

    //checking if input file is defined
    inputFile=$("#inputFileSelector").val();
    console.log(inputFile);
    if(inputFile==""){
        message="File with input data missing";
        showAlert("run",message,"danger");
        return false;
    }

    //checking if param file is defined
    paramOpt=$('input[name="paramFileOpt"]:checked').val();
    console.log(paramOpt);
    if (paramOpt=="file"){
        paramFile=$("#paramFileSelector").val();
        console.log(paramFile);
        if (paramFile==""){
            message="Parameters are to be read from file, but file with parameters not provided";
            showAlert("run",message,"danger");
            return false;
        }
    }

    //checking if initcondfile is defined
    initcondOpt=$('input[name="initcondFileOpt"]:checked').val();
    if (initcondOpt=="file"){
        initcondFile=$("#initcondFileSelector").val();
        if (initcondFile==""){
            message="Initial conditions are to be read from file, but file with initial condition data not provided";
            showAlert("run",message,"danger");
            return false;
        }
    }



    //checking spinup value
    spinup=parseFloat($("#spinup").val());
    nts=parseFloat($("#nts").html());

    if (isNaN(spinup) || !isFinite(spinup) || spinup>5){
        message="Value for spinup should be a numeric value between 0 and 5";
        showAlert("run",message,"danger");
        return false;
    }

    nmons=spinup*12+nts
    if (nmons>maxts){
        message="Maximum number of months that can be simulated (input plus spinup) is "+maxts+". Currently there are "+nmons;
        showAlert("run",message,"danger");
        return false;
    }

    //checking inputs
    nboxes=$("input[name='outputs[]']:checked").length;
    if(nboxes==0){
        message="There should be some outputs selected";
        showAlert("run",message,"danger");
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
                showAlert("run", response, "danger");
                return false;
            }
            if(fileType=="input"){serverinputFile=response;}
            if(fileType=="param"){serverparamFile=response;}
            if(fileType=="initcond"){serverinitcondFile=response;}
        }

        showAlert("run", "All appears to be OK. You can run the model now", "success");
        $("#runmodelButton").removeClass("disabled").removeAttr('disabled');
        modelChecked=true;
    });
});



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
    return promises;
}



$(document).on('click','#runmodelButton', function(event){
    $("#runOutcome").html("");
    showAlert("run","Model running... Please be patient. It takes approx. 1 sec per year of data...", "info");
    form=$("#optForm")[0];
    formdata=new FormData(form);
    spinup=$("#spinup").val();
    var outputs="";
    $('#outputs input:checked').each(function() {
        outputs=outputs+","+$(this).attr('value');
    });
    //console.log(outputs)
    $("#runOutcome").html('<img src="./img/ajax-loader.gif" alt="Calculating...." class=centered>');
    $.ajax({
        url: "runmodel.php?expID="+expID+"&expCode="+expCode+"&spinup="+spinup+"&input="+serverinputFile+"&initcond="+serverinitcondFile+"&param="+serverparamFile+"&outputs="+outputs,
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
            txt="";
            for (line in response){
                txt+=response[line]+"<br>";
            }

            txt=generatePanel(txt,"runout1", false, "Model run log")

            $("#runOutcome").html(txt);

            if (outcome!="success"){
                showAlert("run", outcome, "danger");
                modelRun=false;
            }else{
                showAlert("run", "Model run completed, apparently successfully. Check run log below and see results in the next panel", "success");
                populateResults(expCode);
                modelRun=true;
            }
        }
    });
});




function populateResults(expCode){
    txt="";
    console.log("populate");
    files=$("input[name='outputs[]']:checked");
    nfiles=files.length;
    for(var c=0, len=nfiles; c < len; c++){
        fileCode=files[c].value;
        key=fileCode.split(".")[0];
        ext=outputsList[key][2];
        plotType=outputsList[key][4];
        resultFile=resultsDir+"/"+expID+"/"+expCode+"-"+key+"."+ext;
        txtin="";
        txtin="<div class='input-group'>";
        if(plotType=="timeseries"){
            txtin+="<input type=button class='btn btn-default mx-1 my-1 plotResults btn-custom btn-"+key+"' data-file="+resultFile+" data-key="+key+" id=plot-"+key+" value='Plot data'>";
        }
        txtin+="<input type=button class='btn btn-default mx-1 my-1 previewResults' data-file="+resultFile+" data-key="+key+" id=download-"+key+" value='Preview data'>";
        txtin+="<input type=button class='btn btn-default mx-1 my-1 downloadResults' data-file="+resultFile+" data-key="+key+" id=download-"+key+" value=Download file>";
        txtin+="</div>";
        txtin+="<div id=resultsOutcome-"+key+" class=outcome>";
        txtin+="<div id=resultsOutcome-"+key+"-graph></div>";
        txtin+="<div id=resultsOutcome-"+key+"-data></div>";
        txtin+="</div>";
        txt+=generatePanel(txtin,key+"result",true, outputsList[key][0]);
    }
 
    $("#resultsOutcome").html(txt);
    $("#resultsOutcome").show();
}


$(document).on('click','.downloadResults', function(event){
    resID=this.getAttribute('data-key');
    $(this).blur();
    resultFile=this.getAttribute('data-file');
    var retVal = confirm("Downloading "+resultFile+". Do you want to continue ?");
    if( retVal == true ) {
        window.location.href = resultFile;
        return true;
    }else{
        return false;
    }
});

$(document).on('click','.previewResults', function(event){
    resID=this.getAttribute('data-key');
    $(this).toggleClass("active");
    $(this).blur();
    $('#resultsOutcome-'+resID+"-data").collapse('toggle');
    resultFile=this.getAttribute('data-file');
    if($('#resultsOutcome-'+resID+"-data").html()==""){
        $("#resultsOutcome-"+resID+"-data").html('<img src="./static/img/ajax-loader.gif" alt="Uploading...." class=centered>');
        tmp=resultFile.split(".");
        ext=tmp[tmp.length-1];
        if(ext=="csv"){
            readFile(resultFile, function(rawdata){
                arraydata=parseCSV(rawdata);
                txt="";
                for(var r=0, lenr=arraydata.length; r < lenr; r++){
                    rowdata=arraydata[r];
                    txt+=rowdata+"</br>";
                }
                $("#resultsOutcome-"+resID+"-data").html(txt);
            });
        }else{
                $("#resultsOutcome-"+resID+"-data").html("cannot handle this at the moment");
        }
    }
});



$(document).on('click','.plotResults', function(event){
    resID=this.getAttribute('data-key');
    $(".btn-"+resID).blur();
    $(this).toggleClass("active");
    $('#resultsOutcome-'+resID+"-graph").collapse('toggle');
    resultFile=this.getAttribute('data-file');
    if($('#resultsOutcome-'+resID+"-graph").html()==""){
        $("#resultsOutcome-"+resID+"-graph").html('<img src="./static/img/ajax-loader.gif" alt="Uploading...." class=centered>');
        tmp=resultFile.split(".");
        ext=tmp[tmp.length-1];
        if(ext=="csv"){
            readFile(resultFile, function(rawdata){
                arraydata=parseCSV(rawdata);
                console.log(arraydata);
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
                label=outputsList[resID][0]+"<br>"+outputsList[resID][3];
                title=outputsList[resID][0];;
                outcome=plotTimeSeries("resultsOutcome-"+resID+"-graph", seriesData, title, label);
                if (outcome != true){
                   $("#resultsOutcome-"+resID+"-graph").html("<span class=alert>"+outcome+"</span>");
                };
            });
        }else{
            $("#resultsOutcome-"+resID+"-graph").html("<img src="+resultFile+">");
        }
    }
});



$(document).on('click','.activeInput', function(event){
    if (modelChecked){
        var retVal = confirm("Changing this will reset model output and input validation. Do you want to continue ?");
        if( retVal == true ) {
            resetRun();
            return true;
        }else{
            return false;
        }
    }
});




$(document).on('change','.activeInput', function(event){
    if (modelChecked){
        resetRun();
    }
});


function resetRun(){
    $("#runmodelButton").addClass("disabled").attr('disabled','disabled');
    $("#runAlert").html("");
    $("#runOutcome").html("");
    $("#resultsOutcome").html("");
    $("#resultsAlert").html("");
    modelChecked=false;
    modelRun=false;
}



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
    $("#modelbotContents").hide()
}

function showDocs(){
    $("#docsContents").show()
    $("#modelContents").hide()
    $("#homeContents").hide()
    $("#modelbotContents").hide()
}

function showModel(){
    $("#docsContents").hide()
    $("#modelbotContents").hide()
    $("#modelContents").show()
    $("#homeContents").hide()
}

function showBotModel(){
    $("#docsContents").hide()
    $("#modelbotContents").show()
    $("#modelContents").hide()
    $("#homeContents").hide()
}


function pageinModal(page,title){ 
    $.get("./text/"+page, function(data){
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


$(document).on('click','*[data-pload]', function(e) {
    var ev = $(this);
    e.preventDefault();
    ev.off('hover');
    page="./text/"+this.dataset.pload;
    $.get(page, function(data){
        ev.popover({
            html: true,
            content: data,
            trigger: "focus"
        }).popover('show').parent().on('click', 'a', function(e) {
            e.preventDefault();
            var target = $(this).attr("id");
            pageinModal(target,'');
        });
    });
});


function listsavedExp(){
    txt="<div>";
    txt+="<a>User run ID: <input type=text name=runID id=runID class=activeInput>";
    txt+="</div>";
    $("#selectexpDiv").html(txt).show();
}


$(document).on('keypress', 'form', function(e) {
  console.log("test");
  if (e.keyCode == 13) {               
    e.preventDefault();
    return false;
  }
});



function generatePanel(text, panelID, isin, title){
    if (isin){isin="in"}else{isin=""};
    _txt="<div class='panel panel-default'>";
    _txt+="<div class='panel-heading panel-heading-small'>";
    _txt+="<a data-toggle='collapse' href='#"+panelID+"'>"+title+"</a>";
    _txt+="</div>";
    _txt+="<div id='"+panelID+"' class='panel-collapse collapse "+isin+"'>";
    _txt+="<div class='panel-body'>";
    _txt+="<div id=runlog class='container contained'>";
    _txt+=text;    
    _txt+="</div>";
    _txt+="</div>";
    _txt+="</div>";
    _txt+="</div>";

    return _txt;
}



