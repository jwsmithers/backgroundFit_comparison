import ROOT
from ROOT import gROOT
gROOT.SetBatch(True)

SL_path_stat_only="/eos/user/j/jwsmith/ttgamma/plottingPipeline/v010/11_04_2018/singlelepton_fullFit_merged_C_Off_StatOnly/build/SR1_ejets_mujets_merged/ejets_mujets_merged/Histograms/"
SL_path="/eos/user/j/jwsmith/ttgamma/plottingPipeline/v010/11_04_2018/singlelepton_fullFit_merged_C_Off/build/SR1_ejets_mujets_merged/ejets_mujets_merged/Histograms/"
DL_path="/eos/user/j/jwsmith/ttgamma/plottingPipeline/v010/11_04_2018/dilepton_fullFit_merged_C_Off/build/SR1_ee_mumu_emu_merged/ee_mumu_emu_merged/Histograms/"
DL_path_stat_only="/eos/user/j/jwsmith/ttgamma/plottingPipeline/v010/11_04_2018/dilepton_fullFit_merged_C_Off_StatOnly/build/SR1_ee_mumu_emu_merged/ee_mumu_emu_merged/Histograms/"

HS=3244
alpha=0.3

def plot(channel,ntuplePath,ntuplePath_statOnly,variable,prefitNtuple,xvar):
  prefit=ROOT.TFile(ntuplePath+prefitNtuple,"r")
  postfit=ROOT.TFile(ntuplePath+variable+"_postFit.root","r")
  postfit_stat_only=ROOT.TFile(ntuplePath_statOnly+variable+"_postFit.root","r")

  c1 = ROOT.TCanvas("canvas","",0,0,800,800);
  c1.SetFillColor(0);

  # Upper histogram plot is pad1
  # canvas.cd(1)
  pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
  pad1.SetBottomMargin(0.02)  # joins upper and lower plot
  pad1.Draw()
  # Lower ratio plot is pad2
  pad2 = ROOT.TPad("pad2", "pad2", 0, 0.04, 1, 0.3)
  pad2.SetTopMargin(0.03)  # joins upper and lower plot
  pad2.SetBottomMargin(0.2)
  pad2.Draw()
  pad1.cd()

  hfake = prefit.Get(variable+"_hadronfakes")
  efake = prefit.Get(variable+"_electronfakes")
  other = prefit.Get(variable+"_Other")
  hfake.Add(efake)
  hfake.Add(other)
  if channel=="SL":
    wphoton = prefit.Get(variable+"_Wphoton")
    qcd = prefit.Get(variable+"_QCD")

    hfake.Add(wphoton)
    hfake.Add(qcd)

  if channel=="DL":
    zphoton = prefit.Get(variable+"_Zphoton")
    hfake.Add(zphoton)

  hfake.SetFillStyle(0)
  hfake.SetLineWidth(3)
  hfake.SetLineColor(ROOT.kGreen+1)
  hfake.SetMarkerStyle(0)
  hfake.SetMinimum(0)
  #Common
  hfake.SetTitle("")
  xaxis=hfake.GetXaxis()
  yaxis=hfake.GetYaxis()
  #
  xaxis.SetTitle(xvar)
  xaxis.SetLabelSize(0)
  yaxis.SetTitle("A.U.")
  yaxis.SetTitleOffset(1.7)

  hfake.Sumw2()
  hfake.Scale(1/hfake.Integral())
  Max=hfake.GetMaximum()
  if channel=="SL":
    hfake.SetMaximum(Max+0.03)
  else:
    hfake.SetMaximum(Max+0.3)
  hfake.DrawCopy("hist ")
  hfake.SetFillColorAlpha(ROOT.kGreen+1,alpha)
  hfake.SetFillStyle(HS)
  hfake.Draw("e2same ")



  ####### Now get post-fit
  hfake_post = postfit.Get("h_hadronfakes_postFit")
  efake_post = postfit.Get("h_electronfakes_postFit")
  other_post = postfit.Get("h_Other_postFit")
  hfake_post.Add(efake_post)
  hfake_post.Add(other_post)
  if channel=="SL":
    wphoton_post = postfit.Get("h_Wphoton_postFit")
    qcd_post = postfit.Get("h_QCD_postFit")
    hfake_post.Add(wphoton_post)
    hfake_post.Add(qcd_post)
  if channel=="DL":
    zphoton_post = postfit.Get("h_Zphoton_postFit")
    hfake_post.Add(zphoton_post)
  hfake_post.SetMarkerStyle(0)
  hfake_post.SetLineWidth(3)
  hfake_post.SetFillStyle(0)
  hfake_post.SetLineColor(ROOT.kBlue)
  hfake_post.Sumw2()
  hfake_post.Scale(1/hfake_post.Integral())
  hfake_post.DrawCopy("hist same ")
  hfake_post.SetFillColorAlpha(ROOT.kBlue,alpha)
  hfake_post.SetFillStyle(HS)
  hfake_post.Draw("e2same ")

  # Stat only SL
  hfake_post_stat_only = postfit_stat_only.Get("h_hadronfakes_postFit")
  efake_post_stat_only = postfit_stat_only.Get("h_electronfakes_postFit")
  other_post_stat_only = postfit_stat_only.Get("h_Other_postFit")
  hfake_post_stat_only.Add(efake_post_stat_only)
  hfake_post_stat_only.Add(other_post_stat_only)
  if channel=="SL":
    wphoton_post_stat_only = postfit_stat_only.Get("h_Wphoton_postFit")
    qcd_post_stat_only = postfit_stat_only.Get("h_QCD_postFit")
    hfake_post_stat_only.Add(wphoton_post_stat_only)
    hfake_post_stat_only.Add(qcd_post_stat_only)
  if channel=="DL":
    zphoton_post_stat_only = postfit_stat_only.Get("h_Zphoton_postFit")
    hfake_post_stat_only.Add(zphoton_post_stat_only)

  hfake_post_stat_only.SetFillColor(ROOT.kRed);
  #hfake_post_stat_only.SetFillStyle(3395)
  hfake_post_stat_only.SetFillStyle(0)
  hfake_post_stat_only.SetMarkerStyle(0)
  hfake_post_stat_only.SetLineWidth(3)
  hfake_post_stat_only.SetLineColor(ROOT.kRed)
  if channel=="SL":
    hfake_post_stat_only.Sumw2()
    hfake_post_stat_only.Scale(1/hfake_post_stat_only.Integral())
    hfake_post_stat_only.DrawCopy("hist same ")
    hfake_post_stat_only.SetFillColorAlpha(ROOT.kRed,alpha)
    hfake_post_stat_only.SetFillStyle(HS)
    hfake_post_stat_only.Draw("e2same ")

  lumi = ROOT.TLatex();
  lumi.SetNDC();
  lumi.SetTextAlign(12);
  lumi.SetTextFont(63);
  lumi.SetTextSizePixels(19);
  lumi.DrawLatex(0.4,0.85, "#it{#scale[1.2]{ATLAS}} #bf{Internal}");
  lumi.DrawLatex(0.4,0.8, "#bf{#sqrt{s}=13 TeV, 36.1 fb^{-1}}");
  if channel=="SL":
    lumi.DrawLatex(0.4,0.75,"#bf{Single lepton}")
  else:
    lumi.DrawLatex(0.4,0.75,"#bf{Dilepton}")
  leg = ROOT.TLegend(0.4,0.6,0.55,0.73);
  leg.SetTextSize(0.03);
  leg.AddEntry(hfake,"Pre-fit background","l");
  if channel=="SL":
    leg.AddEntry(hfake_post_stat_only,"Post-fit background, StatOnly","l");
  leg.AddEntry(hfake_post,"Post-fit background","l");

  uncert_legend=hfake.Clone("legend")
  uncert_legend.SetFillColor(1)
  uncert_legend.SetLineColor(0)
  leg.AddEntry(uncert_legend,"Stat error (I think)","f")
  leg.SetBorderSize(0)
  leg.SetFillStyle(0)
  leg.Draw()


   #Ratio plot
  pad2.cd()
  ratio1 = hfake_post.Clone("ratio")
  ratio1.SetFillStyle(0)
  if channel=="SL":
    ratio1.SetMinimum(0.6)
    ratio1.SetMaximum(1.4)
  else:
    ratio1.SetMinimum(0)
    ratio1.SetMaximum(2)
  ratio1.Sumw2()
  ratio1.SetStats(0)
  ratio1.Divide(hfake_post)
  ratio1.SetTitle("")
  y = ratio1.GetYaxis()
  y.SetTitle("#frac{Post-fit}{Pre-fit}")
  y.SetNdivisions(505)
  y.CenterTitle()
  y.SetTitleOffset(1.7)
  x = ratio1.GetXaxis()
  x.SetTitle(xvar)
  x.SetTitleOffset(3.2)
  x.SetLabelSize(21)
  ratio1.SetLineColor(ROOT.kBlue)
  ratio1.DrawCopy("hist ")
  ratio1.SetFillColorAlpha(ROOT.kBlue,alpha);
  ratio1.SetFillStyle(HS)
  ratio1.Draw("e2same ")

  if channel=="SL":
    ratio2 = hfake_post.Clone("ratio_2")
    ratio2.Divide(hfake_post_stat_only)
    ratio2.SetLineColor(ROOT.kRed)
    ratio2.SetFillStyle(0)
    ratio2.DrawCopy("hist same ")
    ratio2.SetFillColorAlpha(ROOT.kRed,alpha)
    ratio2.SetFillStyle(HS)
    ratio2.Draw("e2same ")


  ratio3 = hfake_post.Clone("ratio_3")
  ratio3.Divide(hfake)
  ratio3.SetLineColor(ROOT.kGreen+1)
  ratio3.SetFillStyle(0)
  ratio3.DrawCopy("hist same ")
  ratio3.SetFillColorAlpha(ROOT.kGreen+1,alpha)
  ratio3.SetFillStyle(HS)
  ratio3.Draw("e2same ")

  line = ROOT.TF1("Sig_fa1","1",-1000,1000);
  line.Draw("same")
  line.SetLineColor(ROOT.kBlue);

  c1.SaveAs(variable+"_backgrounds.pdf")



plot("SL",SL_path,SL_path_stat_only, "event_ELD_MVA_ejets","ejets_mujets_merged_event_ELD_MVA_ejets_histos.root","event level descriminator")
plot("SL",SL_path,SL_path_stat_only, "ph_pt_ejets","ejets_mujets_merged_ph_pt_ejets_histos.root","p_{T}(#gamma)")
plot("SL",SL_path,SL_path_stat_only, "ph_eta_ejets","ejets_mujets_merged_ph_eta_ejets_histos.root","#eta(#gamma)")
plot("SL",SL_path,SL_path_stat_only, "dR_lept_ejets","ejets_mujets_merged_dR_lept_ejets_histos.root","#DeltaR(#gamma,l)")

plot("DL",DL_path,DL_path_stat_only, "dEta_lep_ee","ee_mumu_emu_merged_dEta_lep_ee_histos.root","#Delta#eta(l,l)")
plot("DL",DL_path,DL_path_stat_only, "dPhi_lep_ee","ee_mumu_emu_merged_dPhi_lep_ee_histos.root","#Delta#phi(l,l)")
plot("DL",DL_path,DL_path_stat_only, "dR_lept_ee","ee_mumu_emu_merged_dR_lept_ee_histos.root","#DeltaR(#gamma,l)")
plot("DL",DL_path,DL_path_stat_only, "event_ELD_MVA_ee","ee_mumu_emu_merged_event_ELD_MVA_ee_histos.root","event level descriminator")
plot("DL",DL_path,DL_path_stat_only, "ph_pt_ee","ee_mumu_emu_merged_ph_pt_ee_histos.root","p_{T}(#gamma)")
plot("DL",DL_path,DL_path_stat_only, "ph_eta_ee","ee_mumu_emu_merged_ph_eta_ee_histos.root","#eta(#gamma)")

