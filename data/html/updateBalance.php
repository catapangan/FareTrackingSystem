<?php
	$host			= "host=postgres";
	$port			= "port=5432";
	$dbname  		= "dbname=jjc";
	$credentials	= "user=postgres password=jjc2022";
	
	try
	{
		$conn = pg_connect("$host $port $dbname $credentials");
		
		pg_query($conn, "BEGIN");
		
		foreach($_POST as $key => $value)
		{
			//echo $key . "=> " . $value;
			if ($key == 'max_fare' || 
				$key == 'reg_base_fare' || 
				$key == 'spc_base_fare' || 
				$key == 'reg_rate_perkm' || 
				$key == 'spc_rate_perkm'
				)
			{
				$query = "UPDATE settings SET value=$1 WHERE name=$2";
				$result = pg_query_params($conn, $query, array($value, $key));
			}
			else
			{
				$query = "UPDATE user_accounts SET balance=$1, tag=0 WHERE userid=$2";
				$result = pg_query_params($conn, $query, array($value, $key));
			}
		}
		
		pg_query($conn, "COMMIT");
		
		header('Location: index.php');
	}
	catch (Exception $e)
	{
		
	}
?>