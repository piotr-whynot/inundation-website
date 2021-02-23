<?php

$inputFile = $_GET['input'];
$paramFile = $_GET['param'];
$initcondFile = $_GET['initcond'];
$outputs= $_GET['outputs'];
$spinup = $_GET['spinup'];
$expID = $_GET['expID'];
$expCode = $_GET['expCode'];
$domain = $_GET['domain'];

if(isset($_POST) and $_SERVER['REQUEST_METHOD'] == "POST"){
    if($paramFile=="default"){
        $paramFile="model/config/modpar_".$domain.".csv";
    }
    if($initcondFile=="default"){
        $initcondFile="model/config/init_".$domain.".csv";
    }


    //echo $inputFIle.$initcondFile.$paramFile;
    $outputs=explode(",",$outputs);
    $outfiles="";
    foreach($outputs as $output){
        $outfiles=$outfiles." ../public/".$expID."/".$domain."_".$expCode."_".$output;
    }

    chdir("./model");
    $command = escapeshellcmd("/home/piotr/anaconda3/bin/python ./model_".$domain.".py ../".$paramFile." ../".$initcondFile." ../".$inputFile." ".$spinup.$outfiles)." 2>&1";

    $outcome = exec($command, $response);

    $return_arr[] = array("command"=> $command, "outcome" => $outcome,
                    "response" => $response,
    );
    echo json_encode($return_arr);
}
