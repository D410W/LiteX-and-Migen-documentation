/* Machine-generated using Migen */
module top_module(
	input sink_valid,
	output sink_ready,
	input signed [31:0] sink_payload_data,
	output source_valid,
	input source_ready,
	output signed [31:0] source_payload_data
);

wire signed [7:0] relu0_i;
reg signed [7:0] relu0_o;
wire signed [7:0] relu1_i;
reg signed [7:0] relu1_o;
wire signed [7:0] relu2_i;
reg signed [7:0] relu2_o;
wire signed [7:0] relu3_i;
reg signed [7:0] relu3_o;

// synthesis translate_off
reg dummy_s;
initial dummy_s <= 1'd0;
// synthesis translate_on

assign source_valid = sink_valid;
assign sink_ready = source_ready;
assign relu0_i = sink_payload_data[7:0];
assign relu1_i = sink_payload_data[15:8];
assign relu2_i = sink_payload_data[23:16];
assign relu3_i = sink_payload_data[31:24];
assign source_payload_data = {relu3_o, relu2_o, relu1_o, relu0_o};

// synthesis translate_off
reg dummy_d;
// synthesis translate_on
always @(*) begin
	relu0_o <= 8'sd0;
	if (relu0_i[7]) begin
		relu0_o <= 1'd0;
	end else begin
		relu0_o <= relu0_i;
	end
// synthesis translate_off
	dummy_d <= dummy_s;
// synthesis translate_on
end

// synthesis translate_off
reg dummy_d_1;
// synthesis translate_on
always @(*) begin
	relu1_o <= 8'sd0;
	if (relu1_i[7]) begin
		relu1_o <= 1'd0;
	end else begin
		relu1_o <= relu1_i;
	end
// synthesis translate_off
	dummy_d_1 <= dummy_s;
// synthesis translate_on
end

// synthesis translate_off
reg dummy_d_2;
// synthesis translate_on
always @(*) begin
	relu2_o <= 8'sd0;
	if (relu2_i[7]) begin
		relu2_o <= 1'd0;
	end else begin
		relu2_o <= relu2_i;
	end
// synthesis translate_off
	dummy_d_2 <= dummy_s;
// synthesis translate_on
end

// synthesis translate_off
reg dummy_d_3;
// synthesis translate_on
always @(*) begin
	relu3_o <= 8'sd0;
	if (relu3_i[7]) begin
		relu3_o <= 1'd0;
	end else begin
		relu3_o <= relu3_i;
	end
// synthesis translate_off
	dummy_d_3 <= dummy_s;
// synthesis translate_on
end

endmodule

