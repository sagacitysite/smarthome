import * as paper from 'paper';

export class Fireplace {

	// Shorthand for canvas center
	private ct: any;

	// Style for text
	private textStyle: object = {
		fontSize: 25,
		fontFamily: 'Roboto',
		fontWeight: 400,
		fillColor: '#fff'
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
		temperatureAbove: undefined,
		temperatureBelow: undefined
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

		// Draw fireplace
		this.fireplace.inner = this.drawFireplace();
		this.fireplace.temperature = this.drawFireplaceTemperature();
		this.fireplace.flame = this.drawFire();

		// Draw watertank
		this.watertank.tank = this.drawWatertank();
		this.watertank.temperatureAbove = this.drawTemperatureWatertankAbove();
		this.watertank.temperatureBelow = this.drawTemperatureWatertankBelow();

		// Draw flow and pump
		this.flow.pump = this.drawFlowAndPump();
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
	async drawFire() {
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
	 * Temperature watertank above
	 */
	drawTemperatureWatertankAbove() {
		return new paper.PointText({
			point: [this.ct.x+150-15, this.ct.y-60-5],
			content: '00°',
			style: this.textStyle
		});
	}
	
	/**
	 * Temperature watertank below
	 */
	drawTemperatureWatertankBelow() {
		const tempWaterBelow = new paper.PointText({
			point: [this.ct.x+150-15, this.ct.y+60],
			content: '00°',
			style: this.textStyle
		});
	}

	async drawFlowAndPump() {
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
