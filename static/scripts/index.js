function hscroll(text, speed, delay){
	if(speed==undefined||delay==undefined){
		speed = 500;
		delay = 2000;
		} 
	$('#error_header').html('<div id="error_text">'+text+"</div>");
	$('#error_header').slideToggle(speed).delay(delay).slideToggle(speed);
}

function validateRegisterForm(){
	var code = document.forms["register"]["reg_code"].value;
	if (code == null || code == ""){
		hscroll('Please enter code!')
		return false;
	}
}

function validateLoginForm(){
	var email = document.forms["login"]["email"].value;
	var password = document.forms["login"]["password"].value;

	if (email == null || email == ""){
		hscroll('Please enter email')
		return false;
	}

	if (password == null || password == ""){
		hscroll('Please enter password')
		return false;
	}
}

function validateEmail(email) { 
	var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
	return re.test(email);
}

function validatePassword(password) {
	var re = /(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,}/;
	return re.test(password);
}

function validatePhone(p) {
	var phoneRe = /^[2-9]\d{2}[2-9]\d{2}\d{4}$/;
	var digits = p.replace(/\D/g, "");
	return (digits.match(phoneRe) !== null);
}

function validateRegContForm(){
	var regContForm= document.forms["reg_continue"];
	var first_name = regContForm["first_name"].value;
	var last_name  = regContForm["last_name"].value;
	var phone 	   = regContForm["phone"].value;
	var email  	   = regContForm["email"].value;
	var password   = regContForm["password"].value;

	/* First & last name */
	if (first_name == null || first_name == ""){
		hscroll('Please enter a first name.')
		regContForm.first_name.focus();
		return false;
	}

	if (last_name == null || last_name == ""){
		hscroll('Please enter a last name.')
		regContForm.last_name.focus();
		return false;
	}

	/* Phone */
	if (phone == null || phone == ""){
		hscroll('Please enter a phone number.')
		regContForm.phone.focus();
		return false;
	}

	// if (validatePhone(phone) == false) {
	// 	hscroll('Invalid phone number.');
	// 	return false;
	// }

	/* Email */
	if (email == null || email == ""){
		hscroll('Please enter email')
		regContForm.email.focus();
		return false;
	}

	if (validateEmail(email) == false){
		hscroll('Invalid email address.');
		regContForm.email.focus();
		return false;
	}  

	/* Password */
	if (password == null || password == ""){
		hscroll('Please enter password')
		regContForm.password.focus();
		return false;
	}

	if (validatePassword(password) == false){
		hscroll('Passwords must contain at least six characters, including uppercase, lowercase letters and numbers.');
		regContForm.password.focus();
		return false;
	}

}

function validateResetPasswordForm(){
	var passResetForm = document.forms["reset_password_form"];
	var password      = passResetForm["password"].value;

	/* Password */
	if (password == null || password == ""){
		hscroll('Please enter password')
		passResetForm.password.focus();
		return false;
	}

	if (validatePassword(password) == false){
		hscroll('Passwords must contain at least six characters, including uppercase, lowercase letters and numbers.');
		passResetForm.password.focus();
		return false;
	}
}