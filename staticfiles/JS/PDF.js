window.onload = function () {
    document.getElementById("download")
        .addEventListener("click", () => {
            const invoice = document.getElementById("invoice");
            var opt = {
                margin: 0,
                filename: 'file.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2 },
                jsPDF: { unit: 'in', format: 'A4', orientation: 'portrait' }
            };
            html2pdf().from(invoice).set(opt).save();
        });

 document.getElementById("print")
        .addEventListener("click", () => {
            const invoice = document.getElementById("invoice");
            const printWindow = window.open('', '', 'height=600,width=800');
            printWindow.document.write('<html><head><title>Invoice</title>');
            printWindow.document.write('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">'); // Bootstrap CSS
            printWindow.document.write('<style>body{margin: 20px;}</style>'); // Optional custom styles
            printWindow.document.write('</head><body>');
            printWindow.document.write(invoice.innerHTML);
            printWindow.document.write('</body></html>');
            printWindow.document.close();
            printWindow.print();
        });
};

