import * as paper from 'paper';

export class Fireplace {

	// Shorthand for canvas center
	private ct: any;

	// Style for text
	private textStyle: object = {
		fontSize: 25,
		fontFamily: 'Roboto',
		fontWeight: 400,
		fillColor: new paper.Color(235, 235, 235, 0.64)
	};

	private fireplaceSize: any = { w: 120, h: 180 };
	private watertankSize: any = { w: 100, h: 200 };

	// Icons paths
	private fireIconPath: string = 'fire.svg';
	private pumpIconPath: string = 'reload.svg';

	// Store objects for later access
	public fireplace: any = {
		inner: undefined,
		temperature: undefined,
		flame: undefined
	};
	public watertank: any = {
		tank: undefined,
		temperatureTop: undefined,
		temperatureBottom: undefined
	};
	public flow: any = {
		pump: undefined
	}

	/**
	 * Initialize fireplace paper.js drawing
	 */
	constructor(canvas: any) {
		// Setup paper
		paper.setup(canvas);

		// Store view center
		this.ct = paper.view.center
	}

	async build() {
		// Draw fireplace
		this.fireplace.inner = this.drawFireplace();
		this.fireplace.temperature = this.drawFireplaceTemperature();
		this.fireplace.flame = await this.drawFireAsync();

		// Draw watertank
		this.watertank.tank = this.drawWatertank();
		this.watertank.temperatureTop = this.drawTemperatureWatertankTop();
		this.watertank.temperatureBottom = this.drawTemperatureWatertankBottom();

		// Draw flow and pump
		this.flow.pump = await this.drawFlowAndPumpAsync();

		// During loading, we assume the fireplace to be off
		this.isCooling();
		this.stopPump();
	}

	isHeating() {
		this.fireplace.flame.visible = true;
		this.fireplace.inner.fillColor = '#100b08';
	}

	isCooling() {
		this.fireplace.flame.visible = false;
		this.fireplace.inner.fillColor = '#040404';
	}

	startPump() {
		this.flow.pump.visible = true;
	}

	stopPump() {
		this.flow.pump.visible = false;
	}

	setTemperatureFireplace(temperature: number) {
		this.fireplace.temperature.content = `${temperature}°`;
	}

	setTemperatureTankTop(temperature: number) {
		this.watertank.temperatureTop.content = `${temperature}°`;
	}

	setTemperatureTankBottom(temperature: number) {
		this.watertank.temperatureBottom.content = `${temperature}°`;
	}

	/**
	 * Make importSVG from paper.js an async function
	 */
	async importSVGAsync(path: string) {
		return new Promise(function(resolve, reject) {
			paper.project.importSVG(path, function(icon: any) {
				resolve(icon);
			});
		});
	}

	/**
	 * Draw fireplace
	 */
	drawFireplace() {
		// Draw outer fireplace
		const fp = this.fireplaceSize;
		new paper.Path.Rectangle({
			point: [this.ct.x-fp.w/2-150, this.ct.y-fp.h/2],
			size: [fp.w, fp.h],
			fillColor: '#080808',
			strokeColor: '#222222',
			strokeWidth: 5
		});

		// Draw inner fireplace
		const fpIn = { w: 90, h: 90 }
		const fireplaceInner = new paper.Path.Rectangle({
			point: [this.ct.x-fpIn.w/2-150, this.ct.y-fpIn.h/2],
			size: [fpIn.w, fpIn.h],
			fillColor: '#100b08', //'#040404',
			strokeColor: '#222222',
			strokeWidth: 2
		});

		// Return inner fireplace in order to be able to change background color
		return fireplaceInner;
	}

	/**
	 * Temperature fireplace
	 */
	drawFireplaceTemperature() {
		return new paper.PointText({
			point: [this.ct.x-150-15, this.ct.y-60],
			content: '00°',
			style: this.textStyle
		});
	}

	/**
	 * Fire flame icon
	 */
	async drawFireAsync() {
		const fire: any = await this.importSVGAsync(this.fireIconPath);
		fire.scale(2.5);
		fire.position = new paper.Point(this.ct.x-150, this.ct.y+10);

		return fire;
	}

	/**
	 * Draw watertank
	 */
	drawWatertank() {
		const wt = this.watertankSize;
		return new paper.Path.Rectangle({
			point: [this.ct.x-wt.w/2+150, this.ct.y-110],
			size: [wt.w, wt.h],
			fillColor: '#080808',
			strokeColor: '#222222',
			strokeWidth: 5
		});
	}

	/**
	 * Temperature watertank top
	 */
	drawTemperatureWatertankTop() {
		return new paper.PointText({
			point: [this.ct.x+150-15, this.ct.y-60-5],
			content: '00°',
			style: this.textStyle
		});
	}
	
	/**
	 * Temperature watertank bottom
	 */
	drawTemperatureWatertankBottom() {
		return new paper.PointText({
			point: [this.ct.x+150-15, this.ct.y+60],
			content: '00°',
			style: this.textStyle
		});
	}

	async drawFlowAndPumpAsync() {
		// Get all necessary sizes
		const fp = this.fireplaceSize;
		const wt = this.watertankSize;

		// Draw flow and return connection
		new paper.Path.Line({
			from: [this.ct.x+fp.w/2-150, this.ct.y-fp.h/2+20],
			to: [this.ct.x-wt.w/2+150, this.ct.y-fp.h/2+20],
			strokeColor: '#222222',
			strokeWidth: 3
		});
		new paper.Path.Line({
			from: [this.ct.x+fp.w/2-150, this.ct.y+fp.h/2-20],
			to: [this.ct.x-wt.w/2+150, this.ct.y+fp.h/2-20],
			strokeColor: '#222222',
			strokeWidth: 3
		});
		new paper.Path.Line({
			from: [this.ct.x, this.ct.y-fp.h/2+20],
			to: [this.ct.x, this.ct.y+fp.h/2-20],
			strokeColor: '#222222',
			strokeWidth: 3
		});

		// Draw pump
		new paper.Path.Circle({
			center: [this.ct.x, this.ct.y+fp.h/2-20],
			radius: 20,
			fillColor: '#222222'
		});

		// Icon path
		
		const pump: any = await this.importSVGAsync(this.pumpIconPath);
		pump.position = new paper.Point(this.ct.x, this.ct.y+fp.h/2-20);
		paper.view.onFrame = function(event: any) {
			pump.rotate(2);
		}
		//pump.visible = true;

		return pump;
	}
}
