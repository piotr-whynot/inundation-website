<?php
session_start();

if(isset($_POST) and $_SERVER['REQUEST_METHOD'] == "POST"){ 
    $key=array_keys($_FILES)[0];

    $expID=$_GET['expID'];
    $expCode=$_GET['expCode'];

    $path = "public/".$expID."/";

    mkdir($path,0777,true);

    $valid_file_formats = array("csv", "CSV", "Csv");

    $name = $_FILES[$key]['name'];
    $size = $_FILES[$key]['size'];
    if(strlen($name)) {
        list($txt, $ext) = explode(".", $name);
        if(in_array($ext,$valid_file_formats)) {
            if($size<(1024*1024)) {
                $file_name = $expCode."-".$txt.".".$ext;
                $tmp = $_FILES[$key]['tmp_name'];
                $response=$tmp." ".$path.$file_name." ";
                if(move_uploaded_file($tmp, $path.$file_name)){
                    //echo "Upload successful";
                    $response=$path.$file_name;
                    $error=false;
                    $return_arr[] = array("error" => $error,
                    "response" => $response, "fileType"=>$key,
                    );
                    echo json_encode($return_arr);
                }else{
                    $response=$response." Upload failed. Could no move file to target directory. Please report problem to website admin.";
                    $error=true;
                    $return_arr[] = array("error" => $error,
                    "response" => $response, "fileType"=>$key,
                    );
                    echo json_encode($return_arr);
                }
            }else{
                $response="File size maximum 1 MB";
                $error=true;
                $return_arr[] = array("error" => $error,
                    "response" => $response, "fileType"=>$key,
                );
                echo json_encode($return_arr);
            }
        }else{
            $response="Invalid file format";
            $error=true;
            $return_arr[] = array("error" => $error,
                    "response" => $response, "fileType"=>$key,
            );
            echo json_encode($return_arr);
        }
    }else{
        $response="Please select file with required extension ".$ext." ".$name."";
        $outcome=true;
        $return_arr[] = array("error" => $error,
                    "response" => $response, "fileType"=>$key,
        );
        echo json_encode($return_arr);
    }
}
?>
