
// function autocomplete(inp, arr) {
//   /*the autocomplete function takes two arguments,
//   the text field element and an array of possible autocompleted values:*/
//   var currentFocus;
//   var idholder = document.getElementById("id-holder")
//   /*execute a function when someone writes in the text field:*/
//   if(arr.length === 0)  {
//     inp.addEventListener("input", function(e) {
//       var a, b, i, val = this.value;
//       /*close any already open lists of autocompleted values*/
//       closeAllLists();
//       if (!val) { return false;}
//       currentFocus = -1;
//       /*create a DIV element that will contain the items (values):*/
//       a = document.createElement("DIV");
//       a.setAttribute("id", this.id + "autocomplete-list");
//       a.setAttribute("class", "autocomplete-items");
//       /*append the DIV element as a child of the autocomplete container:*/
//       this.parentNode.appendChild(a);
//       /*for each item in the array...*/
      

//       /*create a DIV element for each matching element:*/
//       b = document.createElement("button");
//       /*make the matching letters bold:*/
//       b.type = "button"
//       b.setAttribute("class", "search-btn-borderless text-danger");
//       b.innerHTML = "<strong>" + "We could not find any results!"  + "</strong>";
//       /*insert a input field that will hold the current array item's value:*/
//       // b.innerHTML += "<input type='hidden' value='" + arr[i].name + "'>";
//       /*execute a function when someone clicks on the item value (DIV element):*/
//       a.appendChild(b);

      
//   });
//   }else{
//     inp.addEventListener("input", function(e) {
//       // $("#search-icon").addClass("text-gray-100")
//       $("#search-btn").addClass("rounded-right");
//       $("#search-btn").attr("disabled", true);

//       $("#search-mobile-btn").removeClass("btn-primary")
//       $("#search-mobile-btn").addClass("rounded-right")
//       $("#search-mobile-icon").addClass("text-gray-100")
//       $("#search-mobile-btn").attr("disabled", true);

//       var a, x, s,  b, i, val = this.value;
//       /*close any already open lists of autocompleted values*/
//       closeAllLists();
//       if (!val) { return false;}
//       currentFocus = -1;
//       /*create a DIV element that will contain the items (values):*/
//       a = document.createElement("DIV");
//       a.setAttribute("id", this.id + "autocomplete-list");
//       a.setAttribute("class", "autocomplete-items");
//       /*append the DIV element as a child of the autocomplete container:*/
//       this.parentNode.appendChild(a);
//       /*for each item in the array...*/
      
//       let ismatched =  false
      
//       for (i = 0; i < arr.length; i++) {
//         /*check if the item starts with the same letters as the text field value:*/
//         if (arr[i].name.toUpperCase().includes(val.toUpperCase())) {
//           /*create a DIV element for each matching element:*/
//           ismatched = true;
//           b = document.createElement("button");
//           /*make the matching letters bold:*/
//           b.type = "button"
//           b.setAttribute("class", "search-btn-borderless text-info small");
//           b.id = arr[i].id
//           // b.innerHTML = "<span class='text-dark ml-4'>" +arr[i].group +" : </span>";
//           s = document.createElement("span");
//           s.setAttribute("class", "ml-3");
//           s.innerHTML = "<strong>" + arr[i].name.substr(0, val.length) + "</strong>";
//           s.innerHTML += "<span>" + text_truncate(arr[i].name.substr(val.length),30) + "</span>";
//           b.appendChild(s);
//           x = document.createElement("span");
//           // x.innerHTML += "<strong>" + arr[i].name.substr(0, val.length) + "</strong>";
//           if (arr[i].group == "(vacant)"){var group = "<span class='text-gray-500'>(inactive)</span>"; b.disabled = true; b.classList.add("disabled");}else{var group = arr[i].group;}
//           // x.innerHTML += "<span class='text-black'>" +arr[i].group +"</span>";
//           x.innerHTML += "<span class='text-black'>" + group +"</span>";
//           x.innerHTML += "<span class='ml-1 mr-2 small text-gray-900'>" +arr[i].prop+"</span>";
//           b.appendChild(x);
//           /*insert a input field that will hold the current array item's value:*/
//           b.innerHTML += "<input type='hidden' value='" + arr[i].name + "'>";
          
//           /*execute a function when someone clicks on the item value (DIV element):*/

//           b.addEventListener("click", function(e) {
//               /*insert the value for the autocomplete text field:*/
//               inp.value = this.getElementsByTagName("input")[0].value;


//               idholder.innerHTML = this.id;
//               $("#search-icon").addClass("text-success")
//               $("#search-icon").removeClass("text-light")
//               $("#search-btn").attr("disabled", false);

//               $("#search-mobile-btn").addClass("text-success")
//               $("#search-mobile-btn").removeClass("btn-light")
//               $("#search-mobile-icon").removeClass("text-gray-100")
//               $("#search-mobile-btn").attr("disabled", false);

//               // $("#body-block").addClass("dispnone")
//               // $("#spinner").removeClass("dispnone")
//               $("#preloader-btn").click();
//               $("#barloader").removeClass("dispnone")
//               // $('#result-loader').html('<span class="spinner-border spinner-border mr-2" role="status" aria-hidden="true"></span>Fetching data...');
//               $.ajax({
//                 url: "/results",
//                 type: "get",
//                 data: {id: this.id,initiator:"search"},
//                 success: function(response) {
//                   $("#postloader-btn").click();
//                   $("#barloader").addClass("dispnone")
//                   $("#body-block").addClass("dispnone")
//                   $("#propdisp").addClass("dispnone")
//                   $('#proplist').addClass('dispnone')
//                   $('#searchresults').removeClass('dispnone')



//                   if ($('#content-area').hasClass("isopen") || $('#list-area').hasClass("isopen") || $('#search-area').hasClass("isopen")){
//                     console.log("pass")
//                   } else {
//                     $('#sidebarToggle').click();
//                     $('#smaccordionSidebar').removeClass("toggled");
//                   }


//                   $("#searchresults").html(response);
//                   $("#search-area").addClass("isopen")

//                   if ($("#tenant_identifier").text()){
//                     $.ajax({
//                       url: "/fetch/bills",
//                       type: "get",
//                       data: {
//                         tenantid:  $("#tenant_identifier").text(),
//                         target:"tenant bill"
//                       },
//                       success: function(response) {
                        
//                         $("#search-result-view").html(response);
//                       }
//                     });
//                   }

//                 }
//               });
//               /*close the list of autocompleted values,
//               (or any other open lists of autocompleted values:*/
//               closeAllLists();
//           });
//           a.appendChild(b);
//         }
//       }

//       if(!ismatched){
//           /*create a DIV element for each matching element:*/
//           b = document.createElement("button");
//           /*make the matching letters bold:*/
//           b.type = "button"
//           b.setAttribute("class", "search-btn-borderless text-danger");
//           b.innerHTML = "<strong>" + "We could not find any results!"  + "</strong>";
//           /*insert a input field that will hold the current array item's value:*/
//           // b.innerHTML += "<input type='hidden' value='" + arr[i].name + "'>";
//           /*execute a function when someone clicks on the item value (DIV element):*/
//           a.appendChild(b);      }
//   });
//   }

//   /*execute a function presses a key on the keyboard:*/
//   inp.addEventListener("keydown", function(e) {
//       var x = document.getElementById(this.id + "autocomplete-list");
//       if (x) x = x.getElementsByTagName("button");
//       if (e.keyCode == 40) {
//         /*If the arrow DOWN key is pressed,
//         increase the currentFocus variable:*/
//         currentFocus++;
//         /*and and make the current item more visible:*/
//         addActive(x);
//       } else if (e.keyCode == 38) { //up
//         /*If the arrow UP key is pressed,
//         decrease the currentFocus variable:*/
//         currentFocus--;
//         /*and and make the current item more visible:*/
//         addActive(x);
//       } else if (e.keyCode == 13) {
//         /*If the ENTER key is pressed, prevent the form from being submitted,*/
//         e.preventDefault();
//         if (currentFocus > -1) {
//           /*and simulate a click on the "active" item:*/
//           if (x) x[currentFocus].click();
//         }
//       }
//   });
//   function addActive(x) {
//     /*a function to classify an item as "active":*/
//     if (!x) return false;
//     /*start by removing the "active" class on all items:*/
//     removeActive(x);
//     if (currentFocus >= x.length) currentFocus = 0;
//     if (currentFocus < 0) currentFocus = (x.length - 1);
//     /*add class "autocomplete-active":*/
//     x[currentFocus].classList.add("autocomplete-active");
//   }
//   function removeActive(x) {
//     /*a function to remove the "active" class from all autocomplete items:*/
//     for (var i = 0; i < x.length; i++) {
//       x[i].classList.remove("autocomplete-active");
//     }
//   }
//   function closeAllLists(elmnt) {
//     /*close all autocomplete lists in the document,
//     except the one passed as an argument:*/
//     var x = document.getElementsByClassName("autocomplete-items");
//     for (var i = 0; i < x.length; i++) {
//       if (elmnt != x[i] && elmnt != inp) {
//         x[i].parentNode.removeChild(x[i]);
//       }
//     }
//   }
//   /*execute a function when someone clicks in the document:*/
//   document.addEventListener("click", function (e) {
//       closeAllLists(e.target);
//   });
// }

// $("#search-btn").on('click', function(e) {
            
//   // $("#body-block").addClass("dispnone")
//   // $("#spinner").removeClass("dispnone")
//   $("#preloader-btn").click();
//   $("#barloader").removeClass("dispnone")


//   $.ajax({
//     url: "/results",
//     type: "get",
//     data: {id: $("#id-holder").text(),initiator:"search"},
//     success: function(response) {
//       // $("#spinner").addClass("dispnone")
//       $("#postloader-btn").click();
//       $("#barloader").addClass("dispnone")

//       $("#body-block").addClass("dispnone")
//       $('#proplist').addClass('dispnone')
//       $("#propdisp").addClass("dispnone")
//       $("#searchresults").removeClass("dispnone")


//       if ($('#content-area').hasClass("isopen") || $('#list-area').hasClass("isopen") || $('#search-area').hasClass("isopen")){
//         console.log("pass")
//       } else {
//         $('#sidebarToggle').click();
//         $('#smaccordionSidebar').removeClass("toggled");
//       }

//       $("#searchresults").html(response);
//       $("#search-area").addClass("isopen")
//       if ($("#tenant_identifier").text()){
//         $.ajax({
//           url: "/fetch/bills",
//           type: "get",
//           data: {
//             tenantid:  $("#tenant_identifier").text(),
//             target:"tenant bill"
//           },
//           success: function(response) {
            
//             $("#search-result-view").html(response);
//           }
//         });
//       }
//     }
//   });
// });

// $("#search-mobile-btn").on('click', function(e) {
            
//   // $("#body-block").addClass("dispnone")
//   // $("#spinner").removeClass("dispnone")
//   $("#preloader-btn").click();
//   $("#barloader").removeClass("dispnone")


//   $.ajax({
//     url: "/results",
//     type: "get",
//     data: {id: $("#id-holder").text(),initiator:"search"},
//     success: function(response) {
//       $("#postloader-btn").click();
//       $("#barloader").addClass("dispnone")

//       $("#body-block").addClass("dispnone")
//       $('#proplist').addClass('dispnone')
//       $("#propdisp").addClass("dispnone")
//       // $("#spinner").addClass("dispnone")
      


//       if ($('#content-area').hasClass("isopen") || $('#list-area').hasClass("isopen") || $('#search-area').hasClass("isopen")){
//         console.log("pass")
//       } else {
//         $('#sidebarToggle').click();
//         $('#smaccordionSidebar').removeClass("toggled");
//       }


//       $("#searchresults").removeClass("dispnone")


//       $("#searchresults").html(response);
//       $("#search-area").addClass("isopen")
//       if ($("#tenant_identifier").text()){
//         $.ajax({
//           url: "/fetch/bills",
//           type: "get",
//           data: {
//             tenantid:  $("#tenant_identifier").text(),
//             target:"tenant bill"
//           },
//           success: function(response) {
            
//             $("#search-result-view").html(response);
//           }
//         });
//       }
//     }
//   });
// });

// // const names = ["Peter","Joshua","Kinara"]

// // var results = document.getElementById("suggestions").innerText;
        
// // arr_results = results.split`,`.map(x=>x);




// // $("#searchInput").keyup(function(){
// //     var text = $(this).val();

// //     $.ajax({
// //       url: "/search",
// //       type: "get",
// //       data: {letters: text},
// //       success: function(response) {
// //         $("#suggestions").html(response);
// //         var results = document.getElementById("suggestions").innerText;
        
// //         arr_results = results.split`,`.map(x=>x);

// //         autocomplete(document.getElementById("searchInput"), arr_results);
// //       },
// //       error: function(xhr) {
// //         //Do Something to handle error
// //       }
// //     });
// // });

// // autocomplete(document.getElementById("searchInput"), arr_results);

// text_truncate = function(str, length, ending) {
//   if (length == null) {
//     length = 15;
//   }
//   if (ending == null) {
//     ending = '...';
//   }
//   if (str.length > length) {
//     return str.substring(0, length - ending.length) + ending;
//   } else {
//     return str;
//   }
// };


