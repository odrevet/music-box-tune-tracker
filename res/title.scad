// Add text
module title(text, onSecondSide)
{
	if (onSecondSide>0) {
		mirror ([1,0,-hInset+1]) translate ([-19,10,-hInset+1]) {
                	linear_extrude(height = 1) {
                        	text(text = "REVERSE TITLE", font = "Liberation Sans:style=Bold", size = 3);
			}
		}
		mirror ([1,0,-hInset+1]) translate ([-10,-13,-hInset+1]) {
                	linear_extrude(height = 1) {
                        	text(text = "REVERSE SUBTITLE", font = "Liberation Sans:style=Bold", size = 3);
			}
		}
		translate ([-16,10,-hInset+5]) {
                	linear_extrude(height = 1) {
                        	text(text = "OBVERSE TITLE", font = "Liberation Sans:style=Bold", size = 3);
			}
		}
		translate ([-12,-13,-hInset+5]) {
                	linear_extrude(height = 1) {
                        	text(text = "OBVERSE SUBTITLE", font = "Liberation Sans:style=Bold", size = 3);
			}
		}
	}
}
