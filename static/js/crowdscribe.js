$(document).ready(function(){

    // Shows image preview on screen
    function readURL(input) {

    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            // Change source to uploaded file
            $('#image_being_uploaded').attr('src', e.target.result);
            // change alt text of uploaded image
            $('#image_being_uploaded').attr('alt', "Preview of Uploaded Image")
        }

        reader.readAsDataURL(input.files[0]);
    }
    }

    // Call above function when image uploaded
    $("#document_image_image").change(function(){
        readURL(this);
    });

    // Hide Advanced Search
    $('#advanced').hide()

    // Provides ability to hide and show advanced search
    $('#hide_advanced').click(function(){
        $('#advanced').toggle();
        // Adjust text of hide/show
        if($('#advanced').is(":visible")){
            $('#hide_advanced').text("Hide Advanced Search")
        }
        else{
            $('#hide_advanced').text("Show Advanced Search")
        }
    });

   //var pledge_count = 6;

   $(".tip").tooltip();


   //Hide Time periods when time period is unknown
   if($('#unknown_checkbox').prop('checked')){
        $('#time_period_container').hide();
   }

   else{
        $('#time_period_container').show();
   }

   $('#unknown_checkbox').change(function(){
        $('#time_period_container').toggle();
       });

});
