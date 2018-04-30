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
    #histo.Scale(1/histo.Integral())
  return histo

def getSystematicError(f,binN,channel):
  histograms= []
  f.cd()
  errors = []
  for h in f.GetListOfKeys():
    h = h.ReadObj()
    histograms.append(h.GetName())

  if channel=="SL":
    samples = ["hadronfakes","electronfakes","Wphoton","QCD","Other"]
  elif channel=="DL":
    samples = ["hadronfakes","electronfakes","Zphoton","Other"]
  for s in samples:
    nominal_original=f.Get("h_"+s+"_postFit")
    nominal=nominal_original.Clone("nominal")
    nominal_original.Sumw2()
    nominal.Sumw2()
    for hist in histograms:
      if s not in hist: continue
      if hist == "h_"+s+"_postFit":continue
      if "SigXsecOverSM" in hist: continue
      if "Down" in hist: continue
      if s not in hist: continue
      if "event_ELD_MVA_ejets_ttphoton" in hist:continue
      if "h_tot" in hist: continue
      error=0
      up=f.Get(hist)
      if up.Integral() == 0: continue
      if up.Integral()==nominal.Integral(): continue
      #down=f.Get(hist)
      nbins=up.GetSize()
      up.Sumw2()
      #down.Sumw2()

      #nominal.Scale(1/nominal_original.Integral())
      #up.Scale(1/nominal_original.Integral())

      error = up.GetBinError(binN)
      print hist, " = ", error
      errors.append(error)
  groomed_errors=list(set(errors))
  total_error_list = map(lambda x: x**2,groomed_errors)
  total_error =  math.sqrt(sum(total_error_list))
  print total_error
  return total_error

def plot(channel,ntuplePath,variable,xvar,process):
  postfit=ROOT.TFile(ntuplePath+variable+"_postFit.root","r")
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

  histo_correlated = drawPostPlot(postfit,process,channel,variable,ROOT.kBlue)
  Max=histo_correlated.GetMaximum()
  if channel=="SL":
    histo_correlated.SetMaximum(Max+0.04) # If normalized
    #histo_correlated.SetMaximum(Max+120)
  else:
    histo_correlated.SetMaximum(Max+0.3)
  histo_correlated.DrawCopy("hist")
  histo_correlated.SetFillColorAlpha(ROOT.kBlue,alpha)
  histo_correlated.SetFillStyle(3353)
  histo_correlated.Draw("e2same ")

  # For adding systematics manually:
  histo_uncorrelated = drawPostPlot(postfit,process,channel,variable,ROOT.kRed,manual_error=True)
  histo_uncorrelated.DrawCopy("hist same")
  histo_uncorrelated.SetFillColorAlpha(ROOT.kRed,alpha)
  histo_uncorrelated.SetFillStyle(3335)
  histo_uncorrelated.Draw("e2same ")
  for b in range(1,histo_uncorrelated.GetSize()-1):
    totalBinError = getSystematicError(postfit,b,channel)
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
  leg.AddEntry(total,"Total background","l");

  uncert_cor=histo_correlated.Clone("legend")
  uncert_cor.SetFillColor(ROOT.kBlue)
  uncert_cor.SetLineColor(0)
  uncert_uncor=histo_uncorrelated.Clone("legend2")
  uncert_uncor.SetFillColor(ROOT.kRed)
  uncert_uncor.SetLineColor(0)

  leg.AddEntry(uncert_cor,"Correlated background","f")
  leg.AddEntry(uncert_uncor,"Uncorrelated background","f")
  leg.SetBorderSize(0)
  leg.SetFillStyle(0)
  leg.Draw()


   #Ratio plot
  pad2.cd()
  ratio1 = histo_correlated.Clone("ratio")
  ratio1.SetFillStyle(0)
  if channel=="SL":
    ratio1.SetMinimum(0)
    ratio1.SetMaximum(2)
  else:
    ratio1.SetMinimum(0)
    ratio1.SetMaximum(2)
  ratio1.Sumw2()
  ratio1.SetStats(0)
  ratio1.Divide(histo_correlated)
  ratio1.SetTitle("")
  y = ratio1.GetYaxis()
  y.SetTitle("#frac{Uncorr.}{Corr.}")
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
    #error = (error_uncorr-error_corr)/(error_corr)
    error = (error_uncorr)/(error_corr)
    ratio1.SetBinContent(b,error)
  ratio1.Draw("same hist ")

  line = ROOT.TF1("Sig_fa1","1",-1000,1000);
  line.Draw("same")
  line.SetLineColor(ROOT.kBlack);
  line.SetLineStyle(2);

  c1.SaveAs(variable+"_uncert_comparison.pdf")



plot("SL",SL_Asimov_path, "event_ELD_MVA_ejets","event level descriminator", "background")
#plot("SL",SL_Asimov_path, "ph_pt_ejets","p_{T}(#gamma)", "background")
#plot("SL",SL_Asimov_path, "ph_eta_ejets","#eta(#gamma)","background")
#plot("SL",SL_Asimov_path, "dR_lept_ejets","#DeltaR(#gamma,l)","background")

plot("DL",DL_Asimov_path, "dEta_lep_ee","#Delta#eta(l,l)","background")
#plot("DL",DL_Asimov_path, "dPhi_lep_ee","#Delta#phi(l,l)","background")
#plot("DL",DL_Asimov_path, "dR_lept_ee","#DeltaR(#gamma,l)","background")
#plot("DL",DL_Asimov_path, "event_ELD_MVA_ee","event level descriminator","background")
#plot("DL",DL_Asimov_path, "ph_pt_ee","p_{T}(#gamma)","background")
#plot("DL",DL_Asimov_path, "ph_eta_ee","#eta(#gamma)","background")

