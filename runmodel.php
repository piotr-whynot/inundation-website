<?php

$inputFile = $_GET['input'];
$paramFile = $_GET['param'];
$initcondFile = $_GET['initcond'];
$outputs= $_GET['outputs'];
$spinup = $_GET['spinup'];
$expID = $_GET['expID'];

if(isset($_POST) and $_SERVER['REQUEST_METHOD'] == "POST"){
    if($paramFile=="default"){
        $paramFile="model/config/modpar.dat";
    }
    if($initcondFile=="default"){
        $initcondFile="model/config/init.dat";
    }


    //echo $inputFIle.$initcondFile.$paramFile;
 
    $outfiles="";
    foreach($outputs as $output){
        $outfiles=$outfiles." ../uploads/".$expID."/".$expID."-".$output;
    }

    #$outfile="results/".$sessionID."-".$runID."_alloutflows.csv";

    chdir("./model");
    $command = escapeshellcmd("/home/piotr/anaconda3/bin/python ./hydro_model.py ../".$paramFile." ../".$initcondFile." ../".$inputFile." ".$spinup.$outfiles)." 2>&1";
#    $command= escapeshellcmd("python ./hydro_model.py ../model/config/modpar.dat ../model/config/init.dat ../uploads/31279404-input_1967-2014.csv 0 ../results/31279404-yy_alloutflows.csv");
    #$command= escapeshellcmd("./run.sh");

    $outcome = exec($command, $response);

    $return_arr[] = array("command"=> $command, "outcome" => $outcome,
                    "response" => $response,
    );
    echo json_encode($return_arr);
}
