function setCompanyHealthInsuranceEnabled() {
    let employment_type = document.getElementById('employment_type');
    if (employment_type.value === 'Full-Time')
        document.getElementById('company_ins_opt').disabled = false;
    else
        document.getElementById('company_ins_opt').disabled = true;
}

function setBenefitsEnabled() {
    let employment_type = document.getElementById('employment_type');
    let benefits = document.getElementsByName('benefits');
    benefits.forEach(benefit => {
        benefit.disabled = employment_type.value !== 'Full-Time';
        if (benefit.disabled) benefit.checked = false;
    });
    if (employment_type.value !== 'Full-Time')
        document.getElementById('company_ins_opt').selected = false
}

function formatSSN() {
    let ssn = document.getElementById('ssn');
    let ssnValue = ssn.value;
    if (ssnValue.length === 3 || ssnValue.length === 6)
        ssn.value += '-';
}

function setCompanyInsuranceCheckbox() {
    let checkbox = document.getElementById('Health Insurance');
    if (document.getElementById('health_insurance').value === 'company')
        checkbox.checked = true;
    else checkbox.checked = false;
}

function setCompanyInsuranceOption() {
    let option = document.getElementById('company_ins_opt');
    if (document.getElementById('Health Insurance').checked)
        option.selected = true;
    else option.selected = false;
}
