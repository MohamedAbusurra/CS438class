
document.addEventListener('DOMContentLoaded',  ()  =>  {
  // grab all   file inputs

  const fileInputs = document.querySelectorAll(' input[type="file"] '); 

  //loop through inputs to see file when select
  fileInputs. forEach(input  =>   {


      input.addEventListener('change' , function() {

          if ( this.files &&   this.files.length   >  0 )   {

            // get the label to show the file name
            let fileLabel = this. nextElementSibling  ;

            if (fileLabel) {

                fileLabel.textContent = this.files[0].name ;    // just get first file
            } 
               // TODO: maybe handle muli file later
          }
      });
  });

  let messages = document.querySelectorAll(' .message')   ;


  messages.forEach(  msg =>  {

      // 5 seconds it good
      setTimeout(()  =>  {

         msg.style. display = 'none'; 
      }  ,   5000)  ;

  }) ;
  
 });


