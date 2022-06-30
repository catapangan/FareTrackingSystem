<?php
	$host			= "host=postgres";
	$port			= "port=5432";
	$dbname  		= "dbname=jjc";
	$credentials	= "user=postgres password=jjc2022";
	
	try
	{
		$conn = pg_connect("$host $port $dbname $credentials");
		
		$query = "SELECT * FROM user_accounts";
		$result = pg_query($conn, $query);
		
		$max_fare = 0;
		$reg_base_fare = 0;
		$spc_base_fare = 0;
		$reg_rate_perkm = 0;
		$spc_rate_perkm = 0;
		
		$gps_query = "SELECT * FROM gps_log ORDER BY date DESC LIMIT 1";
		$gps_res = pg_query($conn, $gps_query);
		
		while($row = pg_fetch_assoc($gps_res))
		{
			$gps_lat = $row['lat'];
			$gps_lon = $row['lon'];
			$gps_date = $row['date'];
		}
		
		$settings_query = "SELECT * FROM settings";
		$settings_res = pg_query($conn, $settings_query);
		
		while($row = pg_fetch_assoc($settings_res))
		{
			if ($row['name'] == 'max_fare')
				$max_fare = $row['value'];
			else if ($row['name'] == 'reg_base_fare')
				$reg_base_fare = $row['value'];
			else if ($row['name'] == 'spc_base_fare')
				$spc_base_fare = $row['value'];
			else if ($row['name'] == 'reg_rate_perkm')
				$reg_rate_perkm = $row['value'];
			else if ($row['name'] == 'spc_rate_perkm')
				$spc_rate_perkm = $row['value'];
		}
	}
	catch (Exception $e)
	{
		
	}
?>

<!DOCTYPE html>
<html>
	<head>
		<title>Fare Tracking System</title>
		<!--<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">-->
		
		<script src="js/jquery-3.5.1.js"></script>
		<script src="js/bootstrap.min.js"></script>
		
		<link rel="stylesheet" href="css/bootstrap.css">
		
		<script type="text/javascript">
			function checkFloat(evt)
			{
				var ASCIICode = (evt.which) ? evt.which : evt.keyCode 
				if (ASCIICode > 31 && (ASCIICode < 48 || ASCIICode > 57) && ASCIICode != 46) 
					return false; 
				return true;
			}
			
			function showRegModal()
			{
				$("#reg_status").text("");
				$("#reg_userid").val("");
				$("#reg_firstname").val("");
				$("#reg_lastname").val("");
				$("#regModal").modal("show");
			}
			
			function checkNames()
			{
				if ($("#reg_firstname").val() == "" && 
					$("#reg_lastname").val() == "" && 
					$("#reg_userid").val() == "")
				{
					$("#reg_status").text("All fields cannot be empty");
				}
				else
				{
					$("#regForm").submit();
				}
			}
		</script>
	</head>
	
	<body style="width: 95vw; margin: 3px;">
		<div class="modal fade" id="regModal" tabindex="-1" role="dialog" aria-labelledby="regTitle" aria-hidden="true">
			<div class="modal-dialog" role="document">
				<div class="modal-content">
					<div class="modal-header">
						<h5 class="modal-title" id="regTitle">Add User</h5>
						<button type="button" class="close" data-dismiss="modal" aria-label="Close">
							<span aria-hidden="true">&times;</span>
						</button>
					</div>
					<div class="modal-body">
						<form id="regForm" method="POST" action="registerUser.php">
							<div class="input-group" style="height: 20%; width: 100%;">
								<div class="input-group-prepend" style="height: 100%; width: 30%;">
									<span class="input-group-text" style="width: 100%; font-size: 0.8vw;">ID</span>
								</div>
								<input class="form-control" type="text" name="reg_userid" id="reg_userid" placeholder="Tap RFID" style="width: 50%; font-size: 0.8vw;">
							</div>
							
							<div class="input-group" style="height: 20%; width: 100%;">
								<div class="input-group-prepend" style="height: 100%; width: 30%;">
									<span class="input-group-text" style="width: 100%; font-size: 0.8vw;">First Name</span>
								</div>
								<input class="form-control" type="text" name="reg_firstname" id="reg_firstname" style="width: 70%; font-size: 0.8vw;">
							</div>
							
							<div class="input-group" style="height: 20%; width: 100%;">
								<div class="input-group-prepend" style="height: 100%; width: 30%;">
									<span class="input-group-text" style="width: 100%; font-size: 0.8vw;">Last Name</span>
								</div>
								<input class="form-control" type="text" name="reg_lastname" id="reg_lastname" style="width: 70%; font-size: 0.8vw;">
							</div>
							
							<div class="input-group" style="height: 20%; width: 100%;">
								<div class="input-group-prepend" style="height: 100%; width: 30%;">
									<span class="input-group-text" style="width: 100%; font-size: 0.8vw;">Type</span>
								</div>
								<select class="form-control" name="reg_usertype" id="reg_usertype" style="width: 70%; font-size: 0.8vw;">
									<option value="regular" selected>Regular</option>
									<option value="special">Special</option>
								</select>
							</div>
						</form>
					</div>
					<div class="modal-footer">
						<h6 id="reg_status"></h6>
						<button type="button" class="btn btn-primary" onclick="checkNames()">Register</button>
					</div>
				</div>
			</div>
		</div>
		<div id="content">
			<h1>Fare Tracking System User Accounts</h1>
			<button type="button" class="btn btn-success" onclick="showRegModal()">Add User</button>
			<br>
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
						echo "<tr><td>" . $row['userid'] . "</td><td>" . $row['firstname'] . "</td><td>" . $row['lastname'] . "</td><td><input type=\"text\" name=\"" . $row['userid'] . "\" onkeypress=\"return checkFloat(event)\" value=\"" . $row['balance'] . "\" style=\"width: 20vw\"></td></tr>";
					}
					?>
				</table>
				<br>
				<h3>Last gps location at <?php echo $gps_lat . ", " . $gps_lon; ?> updated on <?php echo $gps_date; ?></h3>
				<br>
				<table border="1" style="width: 100%; table-layout: fixed">
					<tr>
						<th>Setting</th>
						<th>Value</th>
					</tr>
					<tr>
						<td>Max Fare</td>
						<td><input type="text" name="max_fare" value="<?php echo $max_fare; ?>" onkeypress="return checkFloat(event)"></td>
					</tr>
					<tr>
						<td>Regular Base Fare</td>
						<td><input type="text" name="reg_base_fare" value="<?php echo $reg_base_fare; ?>" onkeypress="return checkFloat(event)"></td>
					</tr>
					<tr>
						<td>Special Base Fare</td>
						<td><input type="text" name="spc_base_fare" value="<?php echo $spc_base_fare; ?>" onkeypress="return checkFloat(event)"></td>
					</tr>
					<tr>
						<td>Regular Rate per km</td>
						<td><input type="text" name="reg_rate_perkm" value="<?php echo $reg_rate_perkm; ?>" onkeypress="return checkFloat(event)"></td>
					</tr>
					<tr>
						<td>Special Rate per km</td>
						<td><input type="text" name="spc_rate_perkm" value="<?php echo $spc_rate_perkm; ?>" onkeypress="return checkFloat(event)"></td>
					</tr>
				</table>
				<br>
				<input type="submit" class="btn btn-primary" value="Update All">
			</form>
		</div>
	</body>
</html>