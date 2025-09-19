
document.addEventListener("DOMContentLoaded", function() {
  // CSRF helper
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');

  const BASE_URL = "/resumecheckers";

  // Load job descriptions
  fetch(`${BASE_URL}/api/jobdescriptions/`)
    .then(res => res.json())
    .then(data => {
      if (data.status) {
        let dropdown = document.getElementById("jobDescription");
        data.data.forEach(job => {
          let option = document.createElement("option");
          option.value = job.id;
          option.textContent = job.job_title;
          dropdown.appendChild(option);
        });
      }
    });

  // Handle upload
  document.getElementById("uploadBtn").addEventListener("click", function() {
    let jobId = document.getElementById("jobDescription").value;
    let fileInput = document.getElementById("resumeFile").files[0];

    if (!jobId || !fileInput) {
      alert("Please select job description and upload a resume!");
      return;
    }

    let formData = new FormData();
    formData.append("job_description", jobId);
    formData.append("resume", fileInput);

    let xhr = new XMLHttpRequest();
    xhr.open("POST", `${BASE_URL}/api/analyze-resume/`, true);
    xhr.setRequestHeader("X-CSRFToken", csrftoken);

    xhr.upload.onprogress = function(event) {
      if (event.lengthComputable) {
        let percent = Math.round((event.loaded / event.total) * 100);
        document.getElementById("progress").style.display = "block";
        document.getElementById("uploadPercent").innerText = percent + "%";
        document.getElementById("progressBar").style.width = percent + "%";
      }
    };

    xhr.onload = function() {
      if (xhr.status === 200) {
        let response = JSON.parse(xhr.responseText);
        if (response.status) {
          let data = response.data;
          document.getElementById("rank").innerText = data.rank;
          document.getElementById("experience").innerText = data.total_experience + " years";

          let skillsDiv = document.getElementById("skills");
          skillsDiv.innerHTML = "";
          data.skills.forEach(skill => {
            let span = document.createElement("span");
            span.className = "tag";
            span.textContent = skill;
            skillsDiv.appendChild(span);
          });

          let projDiv = document.getElementById("projects");
          projDiv.innerHTML = "";
          data.project_category.forEach(cat => {
            let span = document.createElement("span");
            span.className = "tag project-tag";
            span.textContent = cat;
            projDiv.appendChild(span);
          });

          document.getElementById("result").style.display = "block";
        } else {
          alert("Error: " + response.message);
        }
      } else {
        alert("Upload failed!");
      }
    };

    xhr.send(formData);
  });
});
