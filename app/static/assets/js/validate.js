
$("#toggle-settings").click(function() {
    let targetDiv = $("#collapsible-settings");
    targetDiv.collapse('toggle');

    // Check if the div is shown, then update the button text accordingly
    if ($(this).text() === "Show less Settings") {
        $(this).text("Show more Settings");
    } else {
        $(this).text("Show less Settings");
    }
});

  const Toast = {
      success(message, Settings = []) {
          this._showToast(message, 'success', Settings);
      },
      danger(message, Settings = []) {
          this._showToast(message, 'danger', Settings);
      },
      warning(message, Settings = []) {
          this._showToast(message, 'warning', Settings);
      },
      info(message, Settings = []) {
          this._showToast(message, 'info', Settings);
      },

      _showToast(message, type, Settings) {
          let duration = Settings.duration || 3000; // Default duration in milliseconds
          let showProgress = Settings.showProgress || false;
          let toastLocation = Settings.toastLocation || 'bottom'; // top / bottom

          const toastContainers = {
              top: document.getElementById('shToastContainerTop'),
              bottom: document.getElementById('shToastContainerBottom'),
          };

          const shToastContainer = toastContainers[toastLocation];
          const toast = document.createElement('div');
          toast.classList.add('sh-toast', type);
          toast.textContent = message;

          const progressBar = document.createElement('div');
          progressBar.classList.add('sh-progress-bar');

          if (showProgress) {
              toast.classList.add('with-sh-progress-bar');
              progressBar.style.width = '0';
              toast.appendChild(progressBar);
          }

          shToastContainer.appendChild(toast);
          // removing previous location and then set new one
          shToastContainer.classList.remove('top', 'bottom');
          shToastContainer.classList.add(toastLocation);

          const startTimestamp = Date.now();

          function updateProgressBar() {
              const elapsedTime = Date.now() - startTimestamp;
              const remainingTime = Math.max(0, duration - elapsedTime);
              const percentage = (remainingTime / duration) * 100;
              progressBar.style.width = `${percentage}%`;

              if (remainingTime > 0) {
                  requestAnimationFrame(updateProgressBar);
              } else {
                  shToastContainer.removeChild(toast);
              }
          }

          requestAnimationFrame(updateProgressBar);
      }


  };


  function toastMaster() {
      let Settings = {
          duration: 1000,
          showProgress: true,
          opacity: 60,
          // toastLocation: 'top'
      };
      Toast.success('+', Settings);
  };

  function toastIt(message, status) {
      let Settings = {
          duration: 6000,
          showProgress: true,
          toastLocation: 'top'
      };
      if (status == 'success') {
          Toast.success(message, Settings);
      } else {
          Toast.danger(message, Settings);
      }
  };



  function validate(...ids) {
    let isValid = true; // Assume all inputs are valid initially

    ids.forEach((id) => {
        const element = document.getElementById(id); // Fetch the element by ID

        // Check if the element has a value property (like an input element)
        if (element && element.value === "") {
            element.style.borderColor = "red"; // Set border color to red for invalid input
            isValid = false; // Set isValid to false if any validation fails
            
            // Find the associated label for the input
            const label = document.querySelector(`label[for="${element.id}"]`);
            const labelText = label ? label.innerText : "This field"; // Extract label text or use a default

            // Create dynamic toast message
            toastIt(`${labelText} is required`, 'danger');
        } else if (element) {
            element.style.borderColor = "green"; // Set border color to green for valid input
        }
    });

    return isValid; // Return true if all are valid, otherwise false
}



  