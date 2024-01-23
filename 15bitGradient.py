import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QColorDialog, QFileDialog,QLineEdit
from PyQt5.QtGui import QColor
import execjs

class GradientGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()
        self.colour1 = QColor(0,0,0)
        self.colour2 = QColor(255,255,255)
        self.gradient_colours = []
        self.gradient_string = ""
        self.num_colours = 16
        
        self.colour_button1 = QPushButton(self.colour1.name())
        self.colour_button1.clicked.connect(self.pick_colour1)
        self.colour_button1.setStyleSheet(f"background-color: {self.colour1.name()}")
        self.colour_button2 = QPushButton(self.colour2.name())
        self.colour_button2.clicked.connect(self.pick_colour2)
        self.colour_button2.setStyleSheet(f"background-color: {self.colour2.name()}")
        self.num_colours_input = QLineEdit()
        self.num_colours_input.setText('16')
        self.gradient_button = QPushButton("Generate Gradient")
        self.gradient_button.clicked.connect(self.generate_gradient)
        self.save_gradient = QPushButton("Save Gradient")
        self.save_gradient.clicked.connect(self.generate_file)
        self.gradient_output = QLineEdit()
        self.gradient_palette = QHBoxLayout()
        vbox.addWidget(self.colour_button1)
        vbox.addWidget(self.colour_button2)
        vbox.addWidget(self.num_colours_input)
        vbox.addWidget(self.gradient_button)
        vbox.addLayout(self.gradient_palette)
        vbox.addWidget(self.save_gradient)
        vbox.addWidget(self.gradient_output)
        self.setLayout(vbox)
        self.generate_gradient()
        self.generate_gradient_labels()
        self.show()
        self.setWindowTitle("15 Bit Gradient")

    def pick_colour1(self):
        self.colour1 = QColorDialog.getColor()
        self.colour_button1.setText(self.colour1.name())
        self.colour_button1.setStyleSheet(f"background-color: {self.colour1.name()}")
    def pick_colour2(self):
        self.colour2 = QColorDialog.getColor()
        self.colour_button2.setText(self.colour2.name())
        self.colour_button2.setStyleSheet(f"background-color: {self.colour2.name()}")

    def reset_palette(self):
        for i in reversed(range(self.gradient_palette.count())): 
            self.gradient_palette.itemAt(i).widget().setParent(None)

    def generate_gradient_labels(self):
        color_labels = [QLabel() for _ in range(self.num_colours)]
        
        # Set background color for each QLabel
        for i in range(self.num_colours):
            color_labels[i].setStyleSheet(f"background-color: {self.gradient_colours[i]}")

        self.reset_palette()
        for label in color_labels:
            self.gradient_palette.addWidget(label)

    def separate_string(self, s):
        return ' '.join([s[i:i+4] for i in range(0, len(s), 4)])

    def generate_gradient(self):
        self.gradient_colours = []
        script = """function cutHex(h) { return (h.charAt(0)=="#") ? h.substring(1,7) : h}
            function checkBin(n){return/^[01]{1,64}$/.test(n)}
            function Bin2Hex(n){if(!checkBin(n))return 0;return parseInt(n,2).toString(16)}
            function PadZero(len, input, str){
                return Array(len-String(input).length+1).join(str||'0')+input;
            }	

            function hexToE(h){
                // get int values of html hex RGB components
                var red = parseInt((cutHex(h)).substring(0,2),16);	
                var green = parseInt((cutHex(h)).substring(2,4),16);
                var blue = parseInt((cutHex(h)).substring(4,6),16)

                // reduce to 5-bit integer values
                red = Math.floor(red/8);
                green = Math.floor(green/8);
                blue = Math.floor(blue/8);

                // convert 5-bit RGB values to binary and combine
                var bR = PadZero(5,red.toString(2));
                var bG = PadZero(5,green.toString(2));
                var bB = PadZero(5,blue.toString(2));
                var bBGR = bB + bG + bR;

                // convert final binary value to hex
                var hfinal = PadZero(4,Bin2Hex(bBGR).toUpperCase());
                return hfinal;
            }
            """
        js_function = execjs.compile(script)
        # Ensure num_colours is at least 2
        num_colours = max(int(self.num_colours_input.text()),2)
        self.num_colours = int(self.num_colours_input.text())
        
        # Calculate the step size for each color component
        step_size_r = (self.colour2.red() - self.colour1.red()) / (num_colours - 1)
        step_size_g = (self.colour2.green() - self.colour1.green()) / (num_colours - 1)
        step_size_b = (self.colour2.blue() - self.colour1.blue()) / (num_colours - 1)

        for i in range(num_colours):
            # Calculate the color components at this step
            current_r = int(self.colour1.red() + i * step_size_r)
            current_g = int(self.colour1.green() + i * step_size_g)
            current_b = int(self.colour1.blue() + i * step_size_b)
            
            # Convert to hex format and append to the result array
            hex_color = "#{:02X}{:02X}{:02X}".format(current_r, current_g, current_b)
            self.gradient_colours.append(hex_color)
        
        self.gradient_string = ""
        for c in self.gradient_colours:
            converted = js_function.call("hexToE",c)
            self.gradient_string+=converted[2:]+converted[:2]

        self.gradient_output.setText(self.separate_string(self.gradient_string))
        self.generate_gradient_labels()
        


    def generate_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save as .nbfp", "", "NBFP Files (*.nbfp);;All Files (*)", options=options)

        with open(file_name,"wb") as file:
            file.write(bytes.fromhex(self.gradient_string))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GradientGenerator()
    sys.exit(app.exec_())
    
