type thLabel = {
    t: string;
    h: string;
}

function thLabelShow(data: thLabel){
    const tLabel = document.getElementById('t_label');
    const hLabel = document.getElementById('h_label');
    if(tLabel !== null){
      tLabel.innerHTML = data.t + '&#x2103;';
    };
    if(hLabel !== null){
      hLabel.innerHTML = data.h + '%';
    };    
}

function fanOnOff(on_off: string){
    const fan = document.getElementById('fan');
    if(fan !== null && on_off === 'High'){
    fan.style.animationDuration = '1s';
    }
    if(fan !== null && on_off === 'Low'){
        fan.style.animationDuration = '0s';
    }
}

function showMessage(msg: string){
   const msg_txtarea = <HTMLTextAreaElement>document.getElementById('message');
   let arr = [];
   arr.unshift(msg);
   if(arr.length > 8){
     arr.pop();
   };
   arr.forEach(elm => {
     msg_txtarea.value += elm + '\r\n';
   });
   msg_txtarea.scrollTop = msg_txtarea.scrollHeight;
}

export { thLabelShow, fanOnOff, showMessage };