"""
This compares an Asimov fit with correlated systematics (just the total error for a bin)
to an asimov fit where the uncertainties have been included by hand (uncorrelated fit)
"""


import ROOT
from ROOT import gROOT
import math
gROOT.SetBatch(True)
import warnings
warnings.filterwarnings("ignore")

SL_Asimov_path="/eos/user/j/jwsmith/ttgamma/plottingPipeline/v010/11_04_2018/singlelepton_Asimov_merged_C_On/build/SR1_ejets_mujets_merged/ejets_mujets_merged/Histograms/"
DL_Asimov_path="/eos/user/j/jwsmith/ttgamma/plottingPipeline/v010/11_04_2018/dilepton_Asimov_merged_C_On/build/SR1_ee_mumu_emu_merged/ee_mumu_emu_merged/Histograms/"

alpha=0.9
normed=True
def drawPostPlot(postfit,process,channel, xvar,colour,manual_error=False):
  colour=ROOT.kBlack
  if process=="background":
    ####### Now get post-fit
    histo = postfit.Get("h_hadronfakes_postFit")
    efake_post = postfit.Get("h_electronfakes_postFit")
    other_post = postfit.Get("h_Other_postFit")
    histo.Add(efake_post)
    histo.Add(other_post)
    if channel=="SL":
      wphoton_post = postfit.Get("h_Wphoton_postFit")
      qcd_post = postfit.Get("h_QCD_postFit")
      histo.Add(wphoton_post)
      histo.Add(qcd_post)
    if channel=="DL":
      zphoton_post = postfit.Get("h_Zphoton_postFit")
      histo.Add(zphoton_post)
  if process=="signal":
    histo = postfit.Get("h_ttphoton_postFit")   
  #############Common
  histo.SetTitle("")
  xaxis=histo.GetXaxis()
  yaxis=histo.GetYaxis()
  xaxis.SetTitle(xvar)
  xaxis.SetLabelSize(0)
  yaxis.SetTitle("A.U.")
  yaxis.SetTitleOffset(1.7)
  ###################
  histo.SetMarkerStyle(0)
  histo.SetLineWidth(3)
  histo.SetFillStyle(0)
  histo.SetLineColor(colour)
  histo.Sumw2()
  normalisation_factor=histo.Integral()
  if normed:
    histo.Scale(1/normalisation_factor)
  return histo,normalisation_factor

def getSystematicError(f,binN,channel,process,variable,total_norm):
  histograms= []
  errors = []

  for h in f.GetListOfKeys():
    histograms.append(h.GetName())

  if process=="signal":
     samples = ["h_ttphoton"]
  elif channel=="SL":
    samples = ["h_hadronfakes","h_electronfakes","h_Wphoton","h_QCD","h_Other"]
  elif channel=="DL":
    samples = ["h_hadronfakes","h_electronfakes","h_Zphoton","h_Other"]
  for s in samples:
    print "Working on: ", s
    for hist in histograms:
      if s not in hist: continue
      if "Down_postFit" in hist: continue
      if "WphotonSF_Up" in hist:continue
      if "SigXsecOverSM" in hist: continue
      postFit_original=f.Get(s+"_postFit")
      postFit=postFit_original.Clone("postFit_original")
      postFit_original.Sumw2()
      postFit.Sumw2()
      if hist == s+"_postFit": continue
      if s not in hist: continue
      if "h_tot" in hist: continue


      error=0
      up=f.Get(hist)
      if up.Integral() == 0: continue
      if up.Integral() == postFit_original.Integral(): continue 
      nbins=up.GetSize()
      up.Sumw2()

      if normed:
        postFit.Scale(1/total_norm)
        up.Scale(1/total_norm)

      #error = up.GetBinError(binN) #Sanity check
      error = up.GetBinContent(binN)-postFit.GetBinContent(binN)
      print s+"_postFit:", binN, " " ,hist, " error = ", error
      errors.append(error)
  # if doing sanity check, only need 1 of the numbers so take a set
  #groomed_errors=list(set(errors)) #sanity check
  groomed_errors=errors
  total_error_list = map(lambda x: x**2,groomed_errors)
  total_error =  math.sqrt(sum(total_error_list))
  return total_error

def plot(channel,ntuplePath,variable,xvar,process):
  postfit=ROOT.TFile(ntuplePath+variable+"_postFit.root","r")
  print "Opened ", ntuplePath+variable+"_postFit.root"
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

  _histo_correlated = drawPostPlot(postfit,process,channel,variable,ROOT.kBlue)
  histo_correlated = _histo_correlated[0]
  Max=histo_correlated.GetMaximum()
  if channel=="SL":
    if normed:
      histo_correlated.SetMaximum(Max+0.04) # If normalized
    else:
      histo_correlated.SetMaximum(Max+120)
  else:
    if normed:
      histo_correlated.SetMaximum(Max+0.05)
    else:
      histo_correlated.SetMaximum(Max+20)
  histo_correlated.DrawCopy("hist")
  histo_correlated.SetFillColorAlpha(ROOT.kBlue,alpha)
  histo_correlated.SetFillStyle(3353)
  histo_correlated.Draw("e2same ")

  # For adding systematics manually:
  _histo_uncorrelated = drawPostPlot(postfit,process,channel,variable,ROOT.kRed,manual_error=True)
  histo_uncorrelated = _histo_uncorrelated[0] 
  norm_factor = _histo_uncorrelated[1] 
  histo_uncorrelated.DrawCopy("hist same")
  histo_uncorrelated.SetFillColorAlpha(ROOT.kRed,alpha)
  histo_uncorrelated.SetFillStyle(3335)
  histo_uncorrelated.Draw("e2same ")
  for b in range(1,histo_uncorrelated.GetSize()-1):
    totalBinError = getSystematicError(postfit,b,channel,process,variable,norm_factor)
    histo_uncorrelated.SetBinError(b,0)
    histo_uncorrelated.SetBinError(b,totalBinError)

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
  total=histo_correlated.Clone("total")
  total.SetLineColor(ROOT.kBlack)
  leg.AddEntry(total,"Total "+process,"l");

  uncert_cor=histo_correlated.Clone("legend")
  uncert_cor.SetFillColor(ROOT.kBlue)
  uncert_cor.SetLineColor(0)
  uncert_uncor=histo_uncorrelated.Clone("legend2")
  uncert_uncor.SetFillColor(ROOT.kRed)
  uncert_uncor.SetLineColor(0)
  leg.AddEntry(uncert_cor,"Correlated "+process+" uncertainties","f")
  leg.AddEntry(uncert_uncor,"Uncorrelated "+process+ " uncertaintes","f")
  leg.SetBorderSize(0)
  leg.SetFillStyle(0)
  leg.Draw()


   #Ratio plot
  pad2.cd()
  ratio1 = histo_correlated.Clone("ratio")
  ratio1.SetFillStyle(0)
  ratio1.Sumw2()
  ratio1.SetStats(0)
  ratio1.Divide(histo_correlated)
  ratio1.SetTitle("")
  y = ratio1.GetYaxis()
  y.SetTitle("#frac{Uncorr. uncert.}{Corr. uncert.}")
  y.SetNdivisions(505)
  y.CenterTitle()
  y.SetTitleOffset(1.7)
  x = ratio1.GetXaxis()
  x.SetTitle(xvar)
  x.SetTitleOffset(3.2)
  x.SetLabelSize(21)
  ratio1.SetLineColor(ROOT.kBlue)
  #ratio1.DrawCopy("hist ")
  ratio1.SetFillColorAlpha(ROOT.kBlue,alpha);
  fill=histo_correlated.GetFillStyle()
  #ratio1.SetFillStyle(fill)
  nbins=ratio1.GetSize()
  for b in range(1,nbins-1):
    error_corr=histo_correlated.GetBinError(b)
    error_uncorr=histo_uncorrelated.GetBinError(b)
    error = (error_uncorr)/(error_corr)
    ratio1.SetBinContent(b,0)
    ratio1.SetBinContent(b,error)
  _max=ratio1.GetBinContent(ratio1.GetMaximumBin())
  _min=ratio1.GetMinimum()
  ratio1.SetMinimum(_min-0.5)
  ratio1.SetMaximum(_max+0.5)
  ratio1.Draw("same hist ")

  line = ROOT.TF1("Sig_fa1","1",-1000,1000);
  line.Draw("same")
  line.SetLineColor(ROOT.kBlack);
  line.SetLineStyle(2);

  c1.SaveAs(variable+"_uncert_comparison_"+process+".pdf")



plot("SL",SL_Asimov_path, "event_ELD_MVA_ejets","event level descriminator", "background")
plot("SL",SL_Asimov_path, "ph_pt_ejets","p_{T}(#gamma)", "background")
plot("SL",SL_Asimov_path, "ph_eta_ejets","#eta(#gamma)","background")
plot("SL",SL_Asimov_path, "dR_lept_ejets","#DeltaR(#gamma,l)","background")

plot("SL",SL_Asimov_path, "event_ELD_MVA_ejets","event level descriminator", "signal")
plot("SL",SL_Asimov_path, "ph_pt_ejets","p_{T}(#gamma)", "signal")
plot("SL",SL_Asimov_path, "ph_eta_ejets","#eta(#gamma)","signal")
plot("SL",SL_Asimov_path, "dR_lept_ejets","#DeltaR(#gamma,l)","signal")

plot("DL",DL_Asimov_path, "dEta_lep_ee","#Delta#eta(l,l)","background")
plot("DL",DL_Asimov_path, "dPhi_lep_ee","#Delta#phi(l,l)","background")
plot("DL",DL_Asimov_path, "dR_lept_ee","#DeltaR(#gamma,l)","background")
plot("DL",DL_Asimov_path, "event_ELD_MVA_ee","event level descriminator","background")
plot("DL",DL_Asimov_path, "ph_pt_ee","p_{T}(#gamma)","background")
plot("DL",DL_Asimov_path, "ph_eta_ee","#eta(#gamma)","background")

plot("DL",DL_Asimov_path, "dEta_lep_ee","#Delta#eta(l,l)","signal")
plot("DL",DL_Asimov_path, "dPhi_lep_ee","#Delta#phi(l,l)","signal")
plot("DL",DL_Asimov_path, "dR_lept_ee","#DeltaR(#gamma,l)","signal")
plot("DL",DL_Asimov_path, "event_ELD_MVA_ee","event level descriminator","signal")
plot("DL",DL_Asimov_path, "ph_pt_ee","p_{T}(#gamma)","signal")
plot("DL",DL_Asimov_path, "ph_eta_ee","#eta(#gamma)","signal")

