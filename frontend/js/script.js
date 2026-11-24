
const API_BASE_URL = "http://127.0.0.1:8000";

// ========================================
// DOM ELEMENTS
// ========================================

const resumeInput = document.getElementById("resumeInput");
const uploadButton = document.getElementById("uploadButton");
const chooseFileButton = document.getElementById("chooseFile");
const submitUploadButton = document.getElementById("submitUpload");
const selectedFileElement = document.getElementById("selectedFile");
const uploadResult = document.getElementById("uploadResult");

// Job matching elements
const jobDescriptionInput = document.getElementById("jobDescription");
const matchJobButton = document.getElementById("matchJobButton");
const jobMatchStatus = document.getElementById("jobMatchStatus");
const jobMatchResult = document.getElementById("jobMatchResult");

// Candidate comparison elements
const candidateOneInput = document.getElementById("candidateOne");
const candidateTwoInput = document.getElementById("candidateTwo");
async function loadUploadedResumes() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/resumes`);

        if (!response.ok) {
            throw new Error("Unable to retrieve uploaded resumes.");
        }

        const data = await response.json();

        // Clear old options while keeping the placeholders
        candidateOneInput.innerHTML =
            '<option value="">Select first candidate</option>';

        candidateTwoInput.innerHTML =
            '<option value="">Select second candidate</option>';

        data.resumes.forEach((resume) => {
            const filename = resume.stored_filename;

            const optionOne = document.createElement("option");
            optionOne.value = filename;
            optionOne.textContent = resume.original_filename || filename;

            const optionTwo = document.createElement("option");
            optionTwo.value = filename;
            optionTwo.textContent = resume.original_filename || filename;

            candidateOneInput.appendChild(optionOne);
            candidateTwoInput.appendChild(optionTwo);
        });

        comparisonStatus.textContent =
            `${data.total_resumes} uploaded resumes available.`;

    } catch (error) {
        console.error("Resume loading error:", error);

        comparisonStatus.textContent =
            "Could not load uploaded resumes. Please check the backend.";
    }
}
loadUploadedResumes();

const comparisonJobDescription =
    document.getElementById("comparisonJobDescription");
const compareCandidatesButton =
    document.getElementById("compareCandidatesButton");
const comparisonStatus =
    document.getElementById("comparisonStatus");
const comparisonResult =
    document.getElementById("comparisonResult");

// Selected resume
let selectedResume = null;


// ========================================
// BACKEND STATUS
// ========================================

async function checkAPIStatus() {

    const statusElement = document.getElementById("apiStatus");

    if (!statusElement) return;

    try {

        const response = await fetch(`${API_BASE_URL}/`);

        if (!response.ok) {
            throw new Error("Backend unavailable");
        }

        const data = await response.json();

        statusElement.textContent =
            data.status === "Running" ? "Online" : "Offline";

        statusElement.style.color =
            data.status === "Running" ? "#20a873" : "#dc3545";

    } catch (error) {

        statusElement.textContent = "Offline";
        statusElement.style.color = "#dc3545";

        console.error("NOVA API Error:", error);
    }
}


// ========================================
// HELPER FUNCTIONS
// ========================================

function getFieldValue(value) {

    if (Array.isArray(value)) {
        return value.length ? getFieldValue(value[0]) : "Not identified";
    }

    if (value && typeof value === "object") {
        return value.value || value.text || "Not identified";
    }

    return value || "Not identified";
}


function createInfoRow(label, value) {

    const row = document.createElement("div");

    row.style.padding = "9px 0";
    row.style.borderBottom = "1px solid #e8eaf1";

    const heading = document.createElement("strong");
    heading.textContent = label + ": ";

    const content = document.createElement("span");
    content.textContent = getFieldValue(value);

    row.append(heading, content);

    return row;
}


// ========================================
// DISPLAY RESUME ANALYSIS
// ========================================

function displayAnalysis(upload, analysisData, analysisError = null) {

    if (!uploadResult) return;

    uploadResult.innerHTML = "";

    const card = document.createElement("div");

    card.style.padding = "18px";
    card.style.background = "#f8faff";
    card.style.border = "1px solid #e1e5f0";
    card.style.borderRadius = "12px";
    card.style.marginTop = "15px";

    const title = document.createElement("h5");

    title.textContent = "NOVA Resume Analysis";
    title.style.color = "#343b68";
    title.style.marginBottom = "15px";

    card.appendChild(title);

    const uploadStatus = document.createElement("p");

    uploadStatus.textContent = "✓ Resume uploaded successfully";
    uploadStatus.style.color = "#20a873";

    card.appendChild(uploadStatus);

    const file = document.createElement("p");

    file.textContent = "File: " + upload.filename;

    card.appendChild(file);

    if (analysisError) {

        const error = document.createElement("p");

        error.textContent = "Analysis error: " + analysisError;
        error.style.color = "#dc3545";

        card.appendChild(error);
        uploadResult.appendChild(card);

        return;
    }

    const analysis = analysisData?.analysis || {};
    const candidate = analysis.candidate || {};

    const status = document.createElement("p");

    status.textContent =
        "Analysis Status: " + (analysis.analysis_status || "Completed");

    status.style.color = "#20a873";

    card.appendChild(status);

    const section = document.createElement("h6");

    section.textContent = "Candidate Information";
    section.style.marginTop = "18px";

    card.appendChild(section);

    const name = candidate.name_candidates?.[0]?.value ||
                 candidate.name ||
                 "Not identified";

    card.appendChild(createInfoRow("Name", name));
    card.appendChild(createInfoRow("Email", candidate.email));
    card.appendChild(createInfoRow("Phone", candidate.phone));

    const skillsHeading = document.createElement("h6");

    skillsHeading.textContent =
        `Extracted Skills (${analysis.total_skills ?? analysis.skills?.length ?? 0})`;

    skillsHeading.style.marginTop = "20px";

    card.appendChild(skillsHeading);

    const skills = analysis.skills || [];

    if (skills.length > 0) {

        skills.forEach(item => {

            const skillBox = document.createElement("div");

            skillBox.style.padding = "10px";
            skillBox.style.margin = "8px 0";
            skillBox.style.background = "#ffffff";
            skillBox.style.border = "1px solid #e5e8f2";
            skillBox.style.borderRadius = "8px";

            const skillName = document.createElement("strong");

            skillName.textContent =
                typeof item === "string" ? item : item.skill;

            skillBox.appendChild(skillName);

            if (item.evidence) {

                const evidence = document.createElement("p");

                evidence.textContent = "Evidence: " + item.evidence;
                evidence.style.fontSize = "12px";
                evidence.style.color = "#777";
                evidence.style.margin = "5px 0";

                skillBox.appendChild(evidence);
            }

            if (item.confidence) {

                const confidence = document.createElement("small");

                confidence.textContent =
                    "Confidence: " + item.confidence;

                confidence.style.color = "#20a873";

                skillBox.appendChild(confidence);
            }

            card.appendChild(skillBox);
        });

    } else {

        const noSkills = document.createElement("p");

        noSkills.textContent = "No skills identified.";

        card.appendChild(noSkills);
    }

    uploadResult.appendChild(card);
}


// ========================================
// SAVED UPLOAD
// ========================================

function getSavedUpload() {

    const savedUpload = sessionStorage.getItem("novaLastUpload");

    if (!savedUpload) return null;

    try {
        return JSON.parse(savedUpload);
    } catch (error) {
        console.error("Saved upload data error:", error);
        return null;
    }
}


// ========================================
// JOB MATCHING HELPERS
// ========================================

function updateJobMatchAvailability() {

    if (!matchJobButton) return;

    const saved = getSavedUpload();

    const hasResume = saved?.upload?.storedFilename;

    matchJobButton.disabled = !hasResume;

    if (jobMatchStatus) {

        jobMatchStatus.textContent = hasResume
            ? "Ready to compare the latest uploaded resume with a job description."
            : "Please upload a resume before starting job matching.";
    }
}


function createSkillList(title, skills, emptyMessage) {

    const section = document.createElement("div");

    section.style.marginTop = "18px";

    const heading = document.createElement("h6");
    heading.textContent = title;

    section.appendChild(heading);

    if (!Array.isArray(skills) || skills.length === 0) {

        const empty = document.createElement("p");

        empty.textContent = emptyMessage;
        empty.style.color = "#777";

        section.appendChild(empty);

        return section;
    }

    const list = document.createElement("div");

    list.style.display = "flex";
    list.style.flexWrap = "wrap";
    list.style.gap = "8px";

    skills.forEach(item => {

        const skillName =
            typeof item === "string" ? item : item.skill;

        const badge = document.createElement("span");

        badge.textContent = skillName;
        badge.style.padding = "7px 12px";
        badge.style.borderRadius = "20px";
        badge.style.fontSize = "13px";
        badge.style.background = "#edf2ff";
        badge.style.color = "#343b68";
        badge.style.border = "1px solid #dce3fa";

        list.appendChild(badge);
    });

    section.appendChild(list);

    return section;
}


// ========================================
// DISPLAY JOB MATCH RESULTS
// ========================================

function displayJobMatch(data) {

    if (!jobMatchResult) return;

    jobMatchResult.innerHTML = "";

    const result = data.result || {};

    const card = document.createElement("div");

    card.style.padding = "20px";
    card.style.background = "#f8faff";
    card.style.border = "1px solid #e1e5f0";
    card.style.borderRadius = "12px";

    const heading = document.createElement("h5");

    heading.textContent = "Job Matching Results";
    heading.style.color = "#343b68";

    card.appendChild(heading);

    const filename = document.createElement("p");

    filename.textContent = "Resume: " + data.filename;

    card.appendChild(filename);

    if (result.total_job_skills === 0) {

        const message = document.createElement("p");

        message.textContent =
            result.message || "No recognized skills found in the job description.";

        message.style.color = "#dc3545";
        message.style.marginTop = "15px";

        card.appendChild(message);

        jobMatchResult.appendChild(card);

        return;
    }

    const score = Number(result.match_score) || 0;

    const scoreHeading = document.createElement("h2");

    scoreHeading.textContent = score + "%";
    scoreHeading.style.color = "#20a873";
    scoreHeading.style.marginTop = "18px";

    card.appendChild(scoreHeading);

    const scoreLabel = document.createElement("p");

    scoreLabel.textContent = "Skill Match Score";

    card.appendChild(scoreLabel);

    const progressBackground = document.createElement("div");

    progressBackground.style.width = "100%";
    progressBackground.style.height = "12px";
    progressBackground.style.background = "#e5e8f2";
    progressBackground.style.borderRadius = "10px";
    progressBackground.style.overflow = "hidden";

    const progress = document.createElement("div");

    progress.style.width = Math.max(0, Math.min(100, score)) + "%";
    progress.style.height = "100%";
    progress.style.background = "#20a873";
    progress.style.borderRadius = "10px";

    progressBackground.appendChild(progress);
    card.appendChild(progressBackground);

    const statistics = document.createElement("div");

    statistics.style.display = "flex";
    statistics.style.flexWrap = "wrap";
    statistics.style.gap = "20px";
    statistics.style.marginTop = "18px";

    const matched = document.createElement("p");

    matched.textContent =
        "Matched Skills: " + result.matched_skill_count;

    const total = document.createElement("p");

    total.textContent =
        "Total Job Skills: " + result.total_job_skills;

    statistics.append(matched, total);

    card.appendChild(statistics);

    card.appendChild(
        createSkillList(
            "Matching Skills",
            result.matching_skills,
            "No matching skills found."
        )
    );

    card.appendChild(
        createSkillList(
            "Missing Skills",
            result.missing_skills,
            "No missing skills identified."
        )
    );

    const note = document.createElement("p");

    note.textContent =
        data.note ||
        "This score represents skill overlap, not an employment decision.";

    note.style.fontSize = "12px";
    note.style.color = "#777";
    note.style.marginTop = "20px";

    card.appendChild(note);

    jobMatchResult.appendChild(card);
}


// ========================================
// JOB DESCRIPTION MATCHING API
// ========================================

if (matchJobButton) {

    matchJobButton.addEventListener("click", async () => {

        const jobDescription = jobDescriptionInput?.value.trim();

        if (!jobDescription) {

            if (jobMatchStatus) {
                jobMatchStatus.textContent =
                    "Please enter a job description first.";

                jobMatchStatus.style.color = "#dc3545";
            }

            return;
        }

        const saved = getSavedUpload();

        const storedFilename = saved?.upload?.storedFilename;

        if (!storedFilename) {

            if (jobMatchStatus) {
                jobMatchStatus.textContent =
                    "Please upload a resume before matching.";

                jobMatchStatus.style.color = "#dc3545";
            }

            updateJobMatchAvailability();

            return;
        }

        matchJobButton.disabled = true;
        matchJobButton.textContent = "Matching...";

        if (jobMatchStatus) {
            jobMatchStatus.textContent =
                "NOVA is comparing resume skills with job requirements...";

            jobMatchStatus.style.color = "#555";
        }

        jobMatchResult.innerHTML = "";

        try {

            const response = await fetch(
                `${API_BASE_URL}/api/resumes/${encodeURIComponent(storedFilename)}/match-job`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        job_description: jobDescription
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Job matching failed."
                );
            }

            displayJobMatch(data);

            if (jobMatchStatus) {
                jobMatchStatus.textContent =
                    "Job matching completed successfully.";

                jobMatchStatus.style.color = "#20a873";
            }

            addActivity(
                "Job description matching completed: " +
                saved.upload.filename
            );

        } catch (error) {

            console.error("NOVA Job Matching Error:", error);

            if (jobMatchStatus) {
                jobMatchStatus.textContent =
                    "Error: " + error.message;

                jobMatchStatus.style.color = "#dc3545";
            }

        } finally {

            matchJobButton.textContent = "Match Resume with Job";

            updateJobMatchAvailability();
        }
    });
}


// ========================================
// CANDIDATE COMPARISON DISPLAY HELPERS
// ========================================

function createComparisonSkillSection(title, skills, emptyMessage) {

    const section = document.createElement("div");

    section.style.marginTop = "16px";

    const heading = document.createElement("h6");
    heading.textContent = title;

    section.appendChild(heading);

    if (!Array.isArray(skills) || skills.length === 0) {

        const empty = document.createElement("p");

        empty.textContent = emptyMessage;
        empty.style.color = "#777";

        section.appendChild(empty);

        return section;
    }

    skills.forEach(item => {

        const skillBox = document.createElement("div");

        skillBox.style.padding = "10px";
        skillBox.style.marginBottom = "8px";
        skillBox.style.background = "#ffffff";
        skillBox.style.border = "1px solid #e5e8f2";
        skillBox.style.borderRadius = "8px";

        const skillName = document.createElement("strong");

        skillName.textContent =
            typeof item === "string" ? item : item.skill;

        skillBox.appendChild(skillName);

        if (item && typeof item === "object" && item.resume_evidence) {

            const evidence = document.createElement("p");

            evidence.textContent =
                "Resume Evidence: " + item.resume_evidence;

            evidence.style.fontSize = "12px";
            evidence.style.color = "#777";
            evidence.style.margin = "5px 0 0";

            skillBox.appendChild(evidence);
        }

        section.appendChild(skillBox);
    });

    return section;
}


function displayCandidateComparison(data) {

    if (!comparisonResult) return;

    comparisonResult.innerHTML = "";

    const results = data.comparison_results || [];

    if (results.length === 0) {

        comparisonResult.textContent =
            "No candidate comparison results were returned.";

        return;
    }

    const pageHeading = document.createElement("h5");

    pageHeading.textContent = "Candidate Comparison Results";
    pageHeading.style.color = "#343b68";
    pageHeading.style.marginBottom = "15px";

    comparisonResult.appendChild(pageHeading);

    const ranking = document.createElement("p");

    ranking.textContent =
        "Ranking Method: " + (data.ranking_method || "Skill coverage");

    comparisonResult.appendChild(ranking);

    results.forEach((candidate, index) => {

        const card = document.createElement("div");

        card.style.padding = "20px";
        card.style.marginBottom = "15px";
        card.style.background = "#f8faff";
        card.style.border = "1px solid #e1e5f0";
        card.style.borderRadius = "12px";

        const heading = document.createElement("h5");

        heading.textContent =
            `Candidate ${index + 1}`;

        heading.style.color = "#343b68";

        card.appendChild(heading);

        const filename = document.createElement("p");

        filename.textContent =
            "Stored Filename: " + candidate.candidate;

        card.appendChild(filename);

        const score = Number(candidate.candidate_score) || 0;

        const scoreHeading = document.createElement("h2");

        scoreHeading.textContent = score + "%";
        scoreHeading.style.color = "#20a873";
        scoreHeading.style.marginTop = "15px";

        card.appendChild(scoreHeading);

        const scoreLabel = document.createElement("p");

        scoreLabel.textContent = "Candidate Skill Match Score";

        card.appendChild(scoreLabel);

        const progressBackground = document.createElement("div");

        progressBackground.style.width = "100%";
        progressBackground.style.height = "12px";
        progressBackground.style.background = "#e5e8f2";
        progressBackground.style.borderRadius = "10px";
        progressBackground.style.overflow = "hidden";

        const progress = document.createElement("div");

        progress.style.width =
            Math.max(0, Math.min(100, score)) + "%";

        progress.style.height = "100%";
        progress.style.background = "#20a873";
        progress.style.borderRadius = "10px";

        progressBackground.appendChild(progress);

        card.appendChild(progressBackground);

        const statistics = document.createElement("p");

        statistics.style.marginTop = "15px";

        statistics.textContent =
            "Matched Skills: " +
            (candidate.matched_skill_count ?? 0) +
            " / " +
            (candidate.total_job_skills ?? 0);

        card.appendChild(statistics);

        card.appendChild(
            createComparisonSkillSection(
                "Matching Skills",
                candidate.matching_skills,
                "No matching skills found."
            )
        );

        card.appendChild(
            createComparisonSkillSection(
                "Missing Skills",
                candidate.missing_skills,
                "No missing skills identified."
            )
        );

        const explanation = document.createElement("p");

        explanation.textContent =
            candidate.scoring_explanation ||
            "No scoring explanation available.";

        explanation.style.marginTop = "15px";
        explanation.style.fontSize = "13px";
        explanation.style.color = "#555";

        card.appendChild(explanation);

        comparisonResult.appendChild(card);
    });

    const note = document.createElement("p");

    note.textContent =
        data.note ||
        "Candidate rankings support recruiter review and are not final hiring decisions.";

    note.style.padding = "12px";
    note.style.background = "#fff8e8";
    note.style.borderRadius = "8px";
    note.style.fontSize = "13px";
    note.style.color = "#755b20";

    comparisonResult.appendChild(note);
}


// ========================================
// CANDIDATE COMPARISON API
// ========================================

if (compareCandidatesButton) {

    compareCandidatesButton.addEventListener("click", async () => {

        const candidateOne = candidateOneInput?.value.trim();
        const candidateTwo = candidateTwoInput?.value.trim();

        const jobDescription =
            comparisonJobDescription?.value.trim();

        if (!candidateOne || !candidateTwo) {

            comparisonStatus.textContent =
                "Please enter both candidate stored filenames.";

            comparisonStatus.style.color = "#dc3545";

            return;
        }

        if (candidateOne === candidateTwo) {

            comparisonStatus.textContent =
                "Please enter two different candidate filenames.";

            comparisonStatus.style.color = "#dc3545";

            return;
        }

        if (!jobDescription) {

            comparisonStatus.textContent =
                "Please enter the job description.";

            comparisonStatus.style.color = "#dc3545";

            return;
        }

        compareCandidatesButton.disabled = true;
        compareCandidatesButton.textContent = "Comparing...";

        comparisonStatus.textContent =
            "NOVA is comparing both candidates against the job requirements...";

        comparisonStatus.style.color = "#555";

        comparisonResult.innerHTML = "";

        try {

            const response = await fetch(
                `${API_BASE_URL}/api/resumes/compare-candidates`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        stored_filenames: [
                            candidateOne,
                            candidateTwo
                        ],
                        job_description: jobDescription
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {

                throw new Error(
                    data.detail || "Candidate comparison failed."
                );
            }

            displayCandidateComparison(data);

            comparisonStatus.textContent =
                "Candidate comparison completed successfully.";

            comparisonStatus.style.color = "#20a873";

            addActivity(
                "Candidate comparison completed: 2 candidates compared."
            );

        } catch (error) {

            console.error("NOVA Candidate Comparison Error:", error);

            comparisonStatus.textContent =
                "Error: " + error.message;

            comparisonStatus.style.color = "#dc3545";

        } finally {

            compareCandidatesButton.disabled = false;

            compareCandidatesButton.innerHTML =
                '<i class="bi bi-people"></i> Compare Candidates';
        }
    });
}


// ========================================
// FILE SELECTION
// ========================================

uploadButton.addEventListener("click", () => {
    resumeInput.click();
});

chooseFileButton.addEventListener("click", () => {
    resumeInput.click();
});


// ========================================
// VALIDATE SELECTED RESUME
// ========================================

resumeInput.addEventListener("change", () => {

    const file = resumeInput.files[0];

    if (!file) return;

    const extension = file.name
        .substring(file.name.lastIndexOf("."))
        .toLowerCase();

    if (![".pdf", ".docx"].includes(extension)) {

        alert("Please select a PDF or DOCX resume.");

        resumeInput.value = "";

        return;
    }

    selectedResume = file;

    selectedFileElement.textContent =
        "Selected: " + file.name;

    submitUploadButton.disabled = false;

    uploadResult.innerHTML = "";

    sessionStorage.removeItem("novaLastUpload");

    updateJobMatchAvailability();

    if (jobMatchResult) {
        jobMatchResult.innerHTML = "";
    }

    if (jobMatchStatus) {
        jobMatchStatus.textContent =
            "Upload the selected resume before matching.";

        jobMatchStatus.style.color = "#777";
    }
});


// ========================================
// UPLOAD AND AUTOMATICALLY ANALYZE RESUME
// ========================================

submitUploadButton.addEventListener("click", async () => {

    if (!selectedResume) {
        alert("Please select a resume first.");
        return;
    }

    const formData = new FormData();

    formData.append("files", selectedResume);

    submitUploadButton.disabled = true;
    submitUploadButton.textContent = "Uploading...";

    uploadResult.textContent = "Uploading resume...";
    uploadResult.style.padding = "15px";

    try {

        // STEP 1: Upload resume
        const uploadResponse = await fetch(
            `${API_BASE_URL}/api/resumes/upload`,
            {
                method: "POST",
                body: formData
            }
        );

        const uploadData = await uploadResponse.json();

        if (!uploadResponse.ok) {
            throw new Error(
                uploadData.detail || "Resume upload failed."
            );
        }

        const result = uploadData.results?.[0];

        if (!result || result.upload_status !== "uploaded") {
            throw new Error("Resume upload was unsuccessful.");
        }

        const uploadInfo = {
            filename: result.filename,
            storedFilename: result.stored_filename,
            extractionStatus: result.extraction_status
        };

        // Save upload information
        sessionStorage.setItem(
            "novaLastUpload",
            JSON.stringify({
                upload: uploadInfo,
                analysisData: null
            })
        );

        updateJobMatchAvailability();

        addActivity("Resume uploaded: " + result.filename);

        uploadResult.textContent =
            "Resume uploaded successfully. NOVA is analysing the candidate...";

        // STEP 2: Automatically analyze uploaded resume
        submitUploadButton.textContent = "Analysing...";

        const analyzeResponse = await fetch(
            `${API_BASE_URL}/api/resumes/${encodeURIComponent(result.stored_filename)}/analyze`,
            {
                method: "POST"
            }
        );

        const analysisData = await analyzeResponse.json();

        if (!analyzeResponse.ok) {
            throw new Error(
                analysisData.detail || "Resume analysis failed."
            );
        }

        // STEP 3: Save analysis result
        sessionStorage.setItem(
            "novaLastUpload",
            JSON.stringify({
                upload: uploadInfo,
                analysisData: analysisData
            })
        );

        // STEP 4: Display analysis
        displayAnalysis(uploadInfo, analysisData);

        addActivity("Resume analysis completed: " + result.filename);

        // Update dashboard counters
        const totalElement = document.getElementById("totalResumes");

        const analyzedElement =
            document.getElementById("analyzedCandidates");

        if (totalElement) {

            const current = Number(totalElement.textContent);

            totalElement.textContent =
                (Number.isFinite(current) ? current : 0) + 1;
        }

        if (
            analyzedElement &&
            analysisData.analysis?.analysis_status === "completed"
        ) {

            const current = Number(analyzedElement.textContent);

            analyzedElement.textContent =
                (Number.isFinite(current) ? current : 0) + 1;
        }

        selectedResume = null;

        resumeInput.value = "";

        selectedFileElement.textContent = "";

        updateJobMatchAvailability();

    } catch (error) {

        console.error("NOVA Upload/Analysis Error:", error);

        const saved = getSavedUpload();

        if (saved) {

            displayAnalysis(
                saved.upload,
                saved.analysisData,
                error.message
            );

        } else {

            uploadResult.textContent = "Error: " + error.message;

            uploadResult.style.color = "#dc3545";
        }

        updateJobMatchAvailability();

    } finally {

        submitUploadButton.disabled = true;

        submitUploadButton.textContent = "Analyze Resume";
    }
});


// ========================================
// RECENT ACTIVITY
// ========================================

function addActivity(message) {

    const activityList = document.getElementById("activityList");

    if (!activityList) return;

    const emptyMessage = activityList.querySelector("p");

    if (emptyMessage) {
        activityList.innerHTML = "";
    }

    const item = document.createElement("div");

    item.className = "activity-item";

    item.textContent = message;

    activityList.prepend(item);
}


// ========================================
// RESTORE PREVIOUS RESULT AFTER REFRESH
// ========================================

document.addEventListener("DOMContentLoaded", async () => {

    checkAPIStatus();

    addActivity("NOVA dashboard initialized.");

    updateJobMatchAvailability();

    const savedUpload = sessionStorage.getItem("novaLastUpload");

    if (!savedUpload) return;

    try {

        const saved = JSON.parse(savedUpload);

        if (saved.analysisData) {

            displayAnalysis(saved.upload, saved.analysisData);

            return;
        }

        uploadResult.textContent =
            "Resume uploaded successfully. Resuming analysis...";

        const response = await fetch(
            `${API_BASE_URL}/api/resumes/${encodeURIComponent(saved.upload.storedFilename)}/analyze`,
            {
                method: "POST"
            }
        );

        const analysisData = await response.json();

        if (!response.ok) {
            throw new Error(
                analysisData.detail || "Resume analysis failed."
            );
        }

        sessionStorage.setItem(
            "novaLastUpload",
            JSON.stringify({
                upload: saved.upload,
                analysisData: analysisData
            })
        );

        displayAnalysis(saved.upload, analysisData);

        addActivity(
            "Resume analysis completed: " + saved.upload.filename
        );

        updateJobMatchAvailability();

    } catch (error) {

        console.error("Analysis recovery error:", error);

        uploadResult.textContent =
            "Analysis error: " + error.message;

        uploadResult.style.color = "#dc3545";

        updateJobMatchAvailability();
    }
});

// =========================================
// NOVA - AI INTERVIEW QUESTION GENERATION
// Independent Module - Module 10
// =========================================

const interviewJobDescription = document.getElementById(
    "interviewJobDescription"
);

const generateInterviewButton = document.getElementById(
    "generateInterviewButton"
);

const interviewStatus = document.getElementById(
    "interviewStatus"
);

const interviewResult = document.getElementById(
    "interviewResult"
);


// Generate personalized interview questions
if (generateInterviewButton) {

    generateInterviewButton.addEventListener("click", async function () {

        const saved = getSavedUpload();

        const storedFilename = saved?.upload?.storedFilename;

        const jobDescription = interviewJobDescription.value.trim();

        // Validate uploaded resume
        if (!storedFilename) {
            interviewStatus.textContent =
                "Please upload a resume before generating interview questions.";
            interviewStatus.className = "text-danger mt-3";
            return;
        }

        // Validate job description
        if (!jobDescription) {
            interviewStatus.textContent =
                "Please enter a job description.";
            interviewStatus.className = "text-danger mt-3";
            return;
        }

        // Prepare UI
        generateInterviewButton.disabled = true;
        generateInterviewButton.textContent = "Generating Questions...";

        interviewStatus.textContent =
            "AI is analyzing the resume and job description. Please wait...";
        interviewStatus.className = "text-primary mt-3";

        interviewResult.replaceChildren();

        try {

            const response = await fetch(
                `${API_BASE_URL}/api/resumes/${encodeURIComponent(storedFilename)}/generate-interview-questions`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        job_description: jobDescription
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Interview question generation failed."
                );
            }

            // Display generation information
            const heading = document.createElement("h5");
            heading.className = "mb-3";
            heading.textContent =
                `Generated Interview Questions (${data.total_questions})`;

            interviewResult.appendChild(heading);

            const method = document.createElement("p");
            method.className = "text-muted";
            method.textContent =
                `Generation Method: ${data.generation_method}`;

            interviewResult.appendChild(method);

            // Display each generated question
            data.questions.forEach((item, index) => {

                const card = document.createElement("div");
                card.className = "card mb-3";

                const cardBody = document.createElement("div");
                cardBody.className = "card-body";

                const category = document.createElement("h6");
                category.className = "text-primary";
                category.textContent =
                    `Question ${index + 1} - ${item.category}`;

                const question = document.createElement("p");
                question.className = "fw-semibold mt-2";
                question.textContent = item.question;

                const purpose = document.createElement("p");
                purpose.className = "text-muted mb-0";
                purpose.textContent = `Purpose: ${item.purpose}`;

                cardBody.appendChild(category);
                cardBody.appendChild(question);
                cardBody.appendChild(purpose);

                card.appendChild(cardBody);
                interviewResult.appendChild(card);

            });

            interviewStatus.textContent =
                "Interview questions generated successfully.";

            interviewStatus.className = "text-success mt-3";

            // Add activity without changing existing activity functionality
            if (typeof addActivity === "function") {
                addActivity("AI interview questions generated successfully.");
            }

        } catch (error) {

            interviewStatus.textContent = error.message;
            interviewStatus.className = "text-danger mt-3";

        } finally {

            generateInterviewButton.disabled = false;
            generateInterviewButton.innerHTML =
                '<i class="bi bi-stars"></i> Generate Interview Questions';

        }

    });

}