<?php
	$host			= "host=postgres";
	$port			= "port=5432";
	$dbname  		= "dbname=jjc";
	$credentials	= "user=postgres password=jjc2022";
	
	try
	{
		$conn = pg_connect("$host $port $dbname $credentials");
		
		pg_query($conn, "BEGIN");
		
		if (!isset($_POST['reg_userid']) || 
			!isset($_POST['reg_firstname']) || 
			!isset($_POST['reg_lastname']) || 
			!isset($_POST['reg_usertype']))
			throw new RuntimeException("", 101);
			
		$query = "INSERT INTO user_accounts (userid, firstname, lastname, usertype, tag, balance) VALUES ($1, $2, $3, $4, 0, 0)";
		$res = pg_query_params($conn, $query, array($_POST['reg_userid'], $_POST['reg_firstname'], $_POST['reg_lastname'], $_POST['reg_usertype']));
		
		pg_query($conn, "COMMIT");
	}
	catch (Exception $e)
	{
	}
	
	header('Location: index.php');
?>