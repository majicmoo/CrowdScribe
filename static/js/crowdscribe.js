
//Exam Number: Y0071297

$(document).ready(function(){

   //var pledge_count = 6;

   $(".tip").tooltip();

   if($('#unknown_checkbox').prop('checked')){
        $('#time_period_container').hide();
   }

   else{
        $('#time_period_container').show();
   }

   $('#unknown_checkbox').change(function(){
        $('#time_period_container').toggle();
       });

   $('#unknown_checkbox_container').click(function(){
       if ($('#unknown_checkbox').is(':checked')){
           $('#unknown_checkbox').prop('checked', false);
           $('#unknown_checkbox').change();
       }
       else{
            $('#unknown_checkbox').prop('checked', true);
            $('#unknown_checkbox').change();
       }

   });

});
