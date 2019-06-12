
$('.form').find('input, textarea').on('keyup blur focus', function(e) {

    var $this = $(this),
        label = $this.prev('label');

    if (e.type === 'keyup') {
        if ($this.val() === '') {
            label.removeClass('active highlight');
        } else {
            label.addClass('active highlight');
        }
    } else if (e.type === 'blur') {
        if ($this.val() === '') {
            label.removeClass('active highlight');
        } else {
            label.removeClass('highlight');
        }
    } else if (e.type === 'focus') {

        if ($this.val() === '') {
            label.removeClass('highlight');
        } else if ($this.val() !== '') {
            label.addClass('highlight');
        }
    }

});

$('.tab a').on('click', function(e) {

    e.preventDefault();

    $(this).parent().addClass('active');
    $(this).parent().siblings().removeClass('active');

    target = $(this).attr('href');

    $('.tab-content > div').not(target).hide();

    $(target).fadeIn(600);

});

function login() {
    var email = $("#log_email").val();
    var pwd = $("#log_pwd").val();
    var sha_pwd = hex_sha1(pwd);

    $.ajax({
        type: "post",
        url: "http://127.0.0.1:5000/login",
        cache:false,
        async:false,
        dataType: "json",
        data: JSON.stringify({ uemail: email, upassword: sha_pwd }),
        success: function(result) {
        	if(result.status!=0){
        	    alert(result.message);
        		window.location.href="main.html?email="+email;
        	}
        	else{
        	    alert(result.message);
            }
        }
    });
};


function signup() {
        var email = $("#email").val();
        var nickname = $("#nickname").val();
    	var pwd = $("#pwd").val();
    	var sha_pwd = hex_sha1(pwd);
    	var username = $("#username").val();
    	//console.log(queryData);
	    $.ajax({
	        type: "post",
	        url: "http://127.0.0.1:5000/register",
	        dataType: "json",
	        data: JSON.stringify({ uemail: email, nickname: nickname, upassword: sha_pwd ,
	         uname : username}),
	        success: function(result) {
	            alert(result.message);
	            window.location.href="main.html?email="+email;
	        }
	    });
}