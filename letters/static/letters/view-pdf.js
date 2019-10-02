const pdfUrl = document.querySelector(".pdf-link")["href"];
const canvas = document.querySelector(".pdf-canvas");

const loadingTask = pdfjsLib.getDocument(pdfUrl);
loadingTask.promise.then(pdf => {
    pdf.getPage(1).then(page => {
        const viewport = page.getViewport({scale: 1});
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
            canvasContext: canvas.getContext('2d'),
            viewport: viewport
        };

        page.render(renderContext)
    });
});