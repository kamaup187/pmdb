
    $(document).ready(function () {
        var next_fs

        $(".next").click(function () {

            var form = $("#msform");
            form.validate({
                errorElement: 'span',
                errorClass: 'error-color',
                highlight: function (element, errorClass, validClass) {
                    $(element).closest('.form-group').addClass("has-error");
                },
                unhighlight: function (element, errorClass, validClass) {
                    $(element).closest('.form-group').removeClass("has-error");
                },
                rules: {
                    pass1: {
                        required: true,
                    },
                    pass2: {
                        required: true,
                        equalTo: '#pass1',
                    },
                    natid: {
                        required: true,
                        minlength: 6,
                        maxlength: 8,
                    },
                    tel1: {
                        required: true,
                        minlength: 10,
                        maxlength: 10,

                    },
                    company: {
                        required: true,
                        minlength: 3,
                    },
                    fname: {
                        required: true,
                        minlength: 3,
                    },
                    lname: {
                        required: true,
                        minlength: 3,
                    },
                    email: {
                        required: true,
                        minlength: 3,
                    },
                    addr1: {
                        required: true,
                        minlength: 3,
                    },
                    terms: {
                        required: true,
                    },

                },
                messages: {
                    natid: {
                        required: "National id is required",
                    },
                    pass1: {
                        required: "Password is required",
                    },
                    pass2: {
                        required: "Password required",
                        equalTo: "Passwords don't match",
                    },
                    company: {
                        required: "Company name is required",
                    },
                    fname: {
                        required: "First name is required",
                    },
                    lname: {
                        required: "Last name is required",
                    },
                    phone: {
                        required: "Valid phone number is required",
                    },
                    email: {
                        required: "Valid email is required",
                    },
                    addr1: {
                        required: "Address is required",
                    },
                    terms: {
                        required: "You must agree to terms and conditions !",
                    },
                }
            });
            if (form.valid() === true) {
                if ($('#personal').hasClass('underline')) {
                    next_fs = $('.gotocompany');
                } else if ($('#company').hasClass("underline")) {
                    next_fs = $('#gotofinish');
                } else if ($("#finish").hasClass("underline")) {
                    next_fs = $('#register')
                }
                next_fs.click();
            }
        });

        $('.previous').click(function () {
            if ($('#company').hasClass("underline")) {
                next_fs = $('#gotopersonal');
            } else if ($('#finish').hasClass("underline")) {
                next_fs = $('.gotocompany');
            }
            next_fs.click();
        });

    });
