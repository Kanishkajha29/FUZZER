document.addEventListener('DOMContentLoaded', () => {
    // Handle section visibility based on user selection
    function toggleSection(id, show) {
        const section = document.getElementById(id);
        section.classList.toggle('hidden', !show);
    }

    // Show/hide custom wordlist upload options based on selection
    function handleWordlistSelection(wordlistSelector, uploadSectionId) {
        const wordlist = document.getElementById(wordlistSelector);
        const uploadSection = document.getElementById(uploadSectionId);

        wordlist.addEventListener('change', () => {
            if (wordlist.value === 'custom') {
                uploadSection.classList.remove('hidden');
            } else {
                uploadSection.classList.add('hidden');
            }
        });
    }

    // Handle the directory fuzzing
    document.getElementById('dirFuzzing').addEventListener('change', (event) => {
        toggleSection('dirWordlistSection', event.target.value === 'yes');
    });

    handleWordlistSelection('dirWordlist', 'dirUploadSection');
    
    // Handle the subdomain fuzzing
    document.getElementById('subdomainFuzzing').addEventListener('change', (event) => {
        toggleSection('subdomainWordlistSection', event.target.value === 'yes');
    });

    handleWordlistSelection('subdomainWordlist', 'subdomainUploadSection');

    // Handle the SQL injection
    document.getElementById('sqlInjection').addEventListener('change', (event) => {
        toggleSection('sqlWordlistSection', event.target.value === 'yes');
    });

    handleWordlistSelection('sqlWordlist', 'sqlUploadSection');

    // Handle the XSS
    document.getElementById('xss').addEventListener('change', (event) => {
        toggleSection('xssWordlistSection', event.target.value === 'yes');
    });

    handleWordlistSelection('xssWordlist', 'xssUploadSection');

    // Handle file inclusion section
    document.getElementById('fileInclusion').addEventListener('change', (event) => {
        toggleSection('fileUploadSection', event.target.value === 'yes');
    });

    handleWordlistSelection('fileUploadOption', 'fileUploadInput');

    // Handle other sections (Security Misconfigurations, Network Scan, Whois, etc.)
    document.getElementById('secMisconfiguration').addEventListener('change', (event) => {
        toggleSection('secMisconfigurationSection', event.target.value === 'yes');
    });

    document.getElementById('networkScan').addEventListener('change', (event) => {
        toggleSection('networkScanSection', event.target.value === 'yes');
    });

    document.getElementById('whoisInfo').addEventListener('change', (event) => {
        toggleSection('whoisInfoSection', event.target.value === 'yes');
    });

    document.getElementById('sslCertInfo').addEventListener('change', (event) => {
        toggleSection('sslCertInfoSection', event.target.value === 'yes');
    });

    document.getElementById('csrfTokens').addEventListener('change', (event) => {
        toggleSection('csrfTokensSection', event.target.value === 'yes');
    });

    // Handle form submission
    document.getElementById('fuzzingForm').addEventListener('submit', (event) => {
        event.preventDefault();
        const targetUrl = document.getElementById('targetUrl').value;
        let output = `Target URL: ${targetUrl}\n`;

        // Collecting user inputs and adding them to output
        if (document.getElementById('dirFuzzing').value === 'yes') {
            output += 'Directory Fuzzing: Yes\n';
            if (document.getElementById('dirWordlist').value === 'custom') {
                output += 'Custom Wordlist: Yes\n';
            }
        }

        // Add more conditions for other sections based on the user's choices...

        document.getElementById('output').textContent = output;
        document.getElementById('outputSection').classList.remove('hidden');
    });
});
