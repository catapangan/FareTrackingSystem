<?php
	$host			= "host=localhost";
	$port			= "port=5432";
	$dbname  		= "dbname=jjc";
	$credentials	= "user=pi password=jjc2022";
	
	try
	{
		$conn = pg_connect("$host $port $dbname $credentials");
		
		foreach($_POST as $key => $value)
		{
			echo $key . "=> " . $value;
			$query = "UPDATE user_accounts SET balance=$1 WHERE userid=$2";
			$result = pg_query_params($conn, $query, array($value, $key));
		}
		
		header('Location: index.php');
	}
	catch (Exception $e)
	{
		
	}
?>