<?php
	$host			= "host=localhost";
	$port			= "port=5432";
	$dbname  		= "dbname=jjc";
	$credentials	= "user=pi password=jjc2022";
	
	try
	{
		$conn = pg_connect("$host $port $dbname $credentials");
		
		$query = "SELECT * FROM user_accounts";
		$result = pg_query($conn, $query);
	}
	catch (Exception $e)
	{
		
	}
?>

<!DOCTYPE html>
<html>
	<head>
		<title>Fare Tracking System</title>
		<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
		<script type="text/javascript">
			function checkFloat(evt)
			{
				var ASCIICode = (evt.which) ? evt.which : evt.keyCode 
				if (ASCIICode > 31 && (ASCIICode < 48 || ASCIICode > 57) && ASCIICode != 46) 
					return false; 
				return true;
			} 
		</script>
	</head>
	
	<body style="width: 95vw">
		<h1>Fare Tracking System User Accounts</h1>
		<form method="POST" action="updateBalance.php" style="width: 100%">
			<table border="3" style="width: 100%; table-layout: fixed">
				<tr>
					<th>ID</th>
					<th>Firstname</th>
					<th>Lastname</th>
					<th>Balance</th>
				</tr>
				
				<?php
				while($row = pg_fetch_assoc($result))
				{
					echo "<tr><td>" . $row['userid'] . "</td><td>" . $row['firstname'] . "</td><td>" . $row['lastname'] . "</td><td><input type=\"number\" name=\"" . $row['userid'] . "\" onkeypress=\"return checkFloat(event)\" value=\"" . $row['balance'] . "\" style=\"width: 20vw\"></td></tr>";
				}
				?>
			</table>
			<br>
			<input type="submit" value="Update Balance">
		</form>
	</body>
</html>