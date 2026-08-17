function e(t,n){return{customHTMLHeadEnd:`<script>
// Funkcja do obliczania sumy i 3%
function calculateRealTime() {
    // Pobierz warto\u015Bci z input\xF3w (zamie\u0144 ID na swoje)
    const input1 = document.getElementById('input1').value || 0;
    const input2 = document.getElementById('input2').value || 0;
    const input3 = document.getElementById('input3').value || 0;
    const input4 = document.getElementById('input4').value || 0;
    
    // Konwertuj na liczby
    const num1 = parseFloat(input1);
    const num2 = parseFloat(input2);
    const num3 = parseFloat(input3);
    const num4 = parseFloat(input4);
    
    // Oblicz sum\u0119
    const sum = num1 + num2 + num3 + num4;
    
    // Oblicz 3%
    const threePercent = sum * 0.03;
    
    // Wy\u015Bwietl wynik (zamie\u0144 'resultText' na ID swojego elementu tekstowego)
    document.getElementById('resultText').innerText = threePercent.toFixed(2);
    
    // Opcjonalnie mo\u017Cesz te\u017C pokaza\u0107 sum\u0119
    // document.getElementById('sumText').innerText = sum.toFixed(2);
}

// Dodaj event listenery do wszystkich input\xF3w
document.getElementById('input1').addEventListener('input', calculateRealTime);
document.getElementById('input2').addEventListener('input', calculateRealTime);
document.getElementById('input3').addEventListener('input', calculateRealTime);
document.getElementById('input4').addEventListener('input', calculateRealTime);

// Wywo\u0142aj funkcj\u0119 na starcie
,
calculateRealTime();
<\/script>`,description:"Whether you're shaping strategy, strengthening culture, or preparing for what's next, the insights gained here can shape your company's direction for years to come.",favicon:"assets/images/57fDI8trhFNmCXCb45SLQ6iWr38.png",robots:"max-image-preview:large",socialImage:"assets/images/3KeDDhfyiHMMwuZHHb8g5ejciI.webp",title:"Orgscale - Your Team Aligned with Your Vision"}}export{e as a};
//# sourceMappingURL=chunk-OM5EN7LG.mjs.map
