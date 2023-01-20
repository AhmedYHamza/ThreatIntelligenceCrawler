const regex = new RegExp('^[a-zA-Z0-9\u0600-\u06FF \.\-]+$',);

function EditKeyword (e) {
  swal(
    {
      title: "Edit Keyword",
      type: "input",
      inputValue: e.value,
      showCancelButton: true,
      closeOnConfirm: false,
      animation: "slide-from-top",
      inputPlaceholder: "Enter Keyword Text",
      showLoaderOnConfirm: true
    },
    function (inputValue) {
      if (inputValue === false) return false;
      if (inputValue === "") {
        swal.showInputError("You need to Add a Text!");
        return false;
      }
      else if (!regex.test(inputValue)){
        swal.showInputError("You can use Numbers, Arabic letters, English letters and (. or -) only!");
        return false;
      }
      
      $.ajax({
        type: "PUT",
        url: "/keywords", 
        dataType: "json",
        data: JSON.stringify({id: e.id, text: inputValue}), 
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        success: function(result){
          swal("Keyword Edited", "Keyword: " + result.keyword, "success");
          setTimeout(()=>{
            window.location.href = "/keywords"
          }, 400)
        }, 
        error: function(result){
          swal({ 
            title: "Error", 
            text: "Something went wrong!",  
            icon: "error",  
            button: "Ok",  
          });  
        }
      });
    }
  );
};

function AddKeyword () {
  swal(
    {
      title: "Add Keyword",
      type: "input",
      showCancelButton: true,
      closeOnConfirm: false,
      animation: "slide-from-top",
      inputPlaceholder: "Enter Keyword Text",
      showLoaderOnConfirm: true  
    },
    function (inputValue) {
      if (inputValue === false) return false;
      if (inputValue === "") {
        swal.showInputError("You need to Add a valid Text!");
        return false;
      }
      else if (!regex.test(inputValue)){
        swal.showInputError("You can use Numbers, Arabic letters, English letters and (. or -) only!");
        return false;
      }
      $.ajax({
        type: "POST",
        url: "/keywords", 
        dataType: "json",
        data: JSON.stringify({text: inputValue}), 
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        success: function(result){
          swal("Keyword Added", "Keyword: " + result.keyword, "success");
          setTimeout(()=>{
            window.location.href = "/keywords"
          }, 400)
          
        }, 
        error: function(result){
          swal({ 
            title: "Error", 
            text: "Something went wrong!",  
            icon: "error",  
            button: "Ok",  
          });  
        }
      });
    }
  );
};

function RemoveKeyword(e) {
  swal(
    {
      title: "Are you sure to remove this item?",
      type: "warning",
      showCancelButton: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonText: "Remove",
      closeOnConfirm: false,
      showLoaderOnConfirm: true 
    },
    function () {
      $.ajax({
        type: "DELETE",
        url: "/keywords", 
        dataType: "json",
        data: JSON.stringify({id: e.id}), 
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        success: function(result){
          swal("Keyword Removed!", "", "success");
          setTimeout(()=>{
            window.location.href = "/keywords"
          }, 400)
        }, 
        error: function(result){
          swal({ 
            title: "Error", 
            text: "Something went wrong!",  
            icon: "error",  
            button: "Ok",  
          });  
        }
      });
      
    }
  );
};

function EditDomain (item) {
  (async () => {
    await Swal.fire({
      title: 'Edit Domain',
      html:
        `<input placeholder="Enter Entity" id="swal-input1" class="swal2-input" value="${item.dataset.entity}">` +
        `<input placeholder="Enter Domain" id="swal-input2" class="swal2-input" value="${item.dataset.domain}">`,
      focusConfirm: false,
      showCancelButton: true,
      preConfirm: () => {
        return new Promise(function (resolve) {
            // Validate input
            if ($('#swal-input1').val() == '' || $('#swal-input2').val() == '' ) {
                Swal.showValidationMessage("Enter a value in both fields"); // Show error when validation fails.
                Swal.enableButtons(); // Enable the confirm button again.
            } 
            else if(!regex.test($('#swal-input2').val()) || !regex.test($('#swal-input1').val())){
              Swal.showValidationMessage("You can use Numbers, Arabic letters, English letters and (. or -) only!"); // Show error when validation fails.
              Swal.enableButtons();
            }
            else {
                Swal.resetValidationMessage(); // Reset the validation message.
                resolve([
                    $('#swal-input1').val(),
                    $('#swal-input2').val()
                ]);
            }
        })
      }
    }).then((result) => {
      if (result.isConfirmed) {
        $.ajax({
          type: "PUT",
          url: "/sensitive-domains", 
          dataType: "json",
          data: JSON.stringify({id: item.id, Entity: result.value[0], Domain: result.value[1]}), 
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          success: function(result){
            swal("Domain Edited", "Domain: " + result.domain, "success");
            setTimeout(()=>{
              window.location.href = "/sensitive-domains"
            }, 400)
          }, 
          error: function(result){
            swal({ 
              title: "Error", 
              text: "Something went wrong!",  
              icon: "error",  
              button: "Ok",  
            });  
          }
        });
      } else if (result.isDenied) {
        Swal.fire('Changes are not saved', '', 'info')
      }
    })

  })()
};

function AddDomain(){
  (async () => {
    await Swal.fire({
      title: 'Add a sensitve domain',
      html:
        '<input placeholder="Enter Entity" id="swal-input1" class="swal2-input">' +
        '<input placeholder="Enter Domain" id="swal-input2" class="swal2-input">',
      focusConfirm: false,
      showCancelButton: true,
      preConfirm: () => {
        return new Promise(function (resolve) {
            // Validate input
            if ($('#swal-input1').val() == '' || $('#swal-input2').val() == '') {
                Swal.showValidationMessage("Enter a value in both fields"); // Show error when validation fails.
                Swal.enableButtons(); // Enable the confirm button again.
            } 
            else if(!regex.test($('#swal-input2').val()) || !regex.test($('#swal-input1').val())){
              Swal.showValidationMessage("You can use Numbers, Arabic letters, English letters and (. or -) only!"); // Show error when validation fails.
              Swal.enableButtons();
            }
            else {
                Swal.resetValidationMessage(); // Reset the validation message.
                resolve([
                    $('#swal-input1').val(),
                    $('#swal-input2').val()
                ]);
            }
        })
      }
    }).then((result) => {
      if (result.isConfirmed) {
        $.ajax({
          type: "POST",
          url: "/sensitive-domains", 
          dataType: "json",
          data: JSON.stringify({Entity: result.value[0], Domain: result.value[1]}), 
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          success: function(result){
            Swal.fire("Domain Added", "Domain: " + result.domain, "success");
            setTimeout(()=>{
              window.location.href = "/sensitive-domains"
            }, 400)
            
          }, 
          error: function(result){
            swal({ 
              title: "Error", 
              text: "Something went wrong!",  
              icon: "error",  
              button: "Ok",  
            });  
          }
        });
        // Swal.fire('Saved!', '', 'success')
      } else if (result.isDenied) {
        Swal.fire('Changes are not saved', '', 'info')
      }
    })

  })()
}

function RemoveDomain(e) {
  (async () => {
    await Swal.fire({
      title: "Are you sure to remove this item?",
      type: "warning",
      showCancelButton: true,
      confirmButtonColor: "#DD6B55",
      confirmButtonText: "Remove"
    }).then((result) => {
      if (result.isConfirmed) {
        $.ajax({
          type: "DELETE",
          url: "/sensitive-domains", 
          dataType: "json",
          data: JSON.stringify({id: e.id}), 
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          success: function(result){
            Swal.fire("Domain Removed!", "", "success");
            setTimeout(()=>{
              window.location.href = "/sensitive-domains"
            }, 400)
            
          }, 
          error: function(result){
            swal({ 
              title: "Error", 
              text: "Something went wrong!",  
              icon: "error",  
              button: "Ok",  
            });  
          }
        });
        // Swal.fire('Saved!', '', 'success')
      } else if (result.isDenied) {
        Swal.fire('Changes are not saved', '', 'info')
      }
    })

  })()
}