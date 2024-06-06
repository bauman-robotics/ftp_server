
var dragAndDropBox = document.getElementById("drag-and-drop-box");
var dragAndDropH1 = document.getElementById("drag-and-drop-h1");


// Add the "dragover" event listener
dragAndDropBox.addEventListener("dragover", function (e) {
    e.preventDefault();
    e.stopPropagation();
    dragAndDropBox.style.border = "2px solid #09f";
});

// Add the "dragleave" event listener
dragAndDropBox.addEventListener("dragleave", function (e) {
    e.preventDefault();
    e.stopPropagation();
    dragAndDropBox.style.border = "2px dashed #ccc";
});

// Add the "drop" event listener
dragAndDropBox.addEventListener("drop", function (e) {
    e.preventDefault();
    e.stopPropagation();
    dragAndDropBox.style.border = "2px dashed #ccc";
    var files = e.dataTransfer.files;
    document.getElementById("file").files = files;

});

dragAndDropH1.addEventListener("click", function (e) {
    e.preventDefault();
    e.stopPropagation();

    document.getElementById("file").click();

});

function uploadFile() {
    const fileInput = document.getElementById('file');
    if (fileInput.files.length === 0) {
      alert('Please select a file before uploading');
    } else {
      // code to handle file upload goes here
    }
  }


