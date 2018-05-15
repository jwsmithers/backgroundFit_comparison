"""
This compares a fit with correlated systematics (just the total error for a bin)
to an asimov fit where the uncertainties have been included by hand (uncorrelated fit)
"""


import ROOT
from ROOT import gROOT
import math
gROOT.SetBatch(True)
import warnings
warnings.filterwarnings("ignore")

SL_path="/eos/user/j/jwsmith/ttgamma/plottingPipeline/v010/11_04_2018/singlelepton_fullFit_merged_C_On/build/SR1_ejets_mujets_merged/ejets_mujets_merged/Histograms/"
DL_path="/eos/user/j/jwsmith/ttgamma/plottingPipeline/v010/11_04_2018/dilepton_fullFit_merged_C_On/build/SR1_ee_mumu_emu_merged/ee_mumu_emu_merged/Histograms/"

alpha=0.9
normed=False

def drawPlots(ntupleFile,process,channel,xvar,colour,fit):
  colour=ROOT.kBlack
  f = ROOT.TFile(ntupleFile,"r")
  ROOT.gROOT.cd()

  if fit=="postfit":
    prefix="h_"
    suffix="_postFit"
    print "Using postfit"
  else:
    prefix=xvar+"_"
    suffix=""
    print "Using prefit"

  if process=="background":
    ####### Now get post-fit
    #for h in ntupleFile.GetListOfKeys():
    #  print(h.GetName())
    histo_clone = f.Get(prefix+"hadronfakes"+suffix)
    histo=histo_clone.Clone("cloned hist")
    efake_post = f.Get(prefix+"electronfakes"+suffix)
    other_post = f.Get(prefix+"Other"+suffix)
    histo.Add(efake_post)
    histo.Add(other_post)
    if channel=="SL":
      wphoton_post = f.Get(prefix+"Wphoton"+suffix)
      qcd_post = f.Get(prefix+"QCD"+suffix)
      histo.Add(wphoton_post)
      histo.Add(qcd_post)
    if channel=="DL":
      zphoton_post = f.Get(prefix+"Zphoton"+suffix)
      histo.Add(zphoton_post)
  if process=="signal":
    histo_clone = f.Get(prefix+"ttphoton"+suffix)   
    histo=histo_clone.Clone("cloned_signal_hist")
  #############Common
  histo.SetTitle("")
  xaxis=histo.GetXaxis()
  yaxis=histo.GetYaxis()
  xaxis.SetTitle(xvar)
  xaxis.SetLabelSize(0)
  yaxis.SetTitleOffset(1.7)
  yaxis.SetTitle("Events")
  ###################
  histo.SetMarkerStyle(0)
  histo.SetLineWidth(3)
  histo.SetFillStyle(0)
  histo.SetLineColor(colour)
  histo.Sumw2()
  normalisation_factor=histo.Integral()
  if normed:
    yaxis.SetTitle("A.U.")
    histo.Scale(1/normalisation_factor)
  f.Close()
  return histo,normalisation_factor


def getPostFitSystematicError(f,binN,channel,process,variable, norm_factor):
  File = ROOT.TFile(f,"r")
  ROOT.gROOT.cd()
  histograms= []
  errors = []

  for h in File.GetListOfKeys():
    histograms.append(h.GetName())

  if process=="signal":
     samples = ["h_ttphoton"]
  elif channel=="SL":
    samples = ["h_hadronfakes","h_electronfakes","h_Wphoton","h_QCD","h_Other"]
  elif channel=="DL":
    samples = ["h_hadronfakes","h_electronfakes","h_Zphoton","h_Other"]
  for s in samples:
    for hist in histograms:
      if s not in hist: continue
      if "Down_postFit" in hist: continue
      if "WphotonSF_Up" in hist:continue
      if "SigXsecOverSM" in hist: continue
      postFit_original=File.Get(s+"_postFit")
      postFit_original.Sumw2()
      postFit=postFit_original.Clone("postFit_original")
      if hist == s+"_postFit": continue
      if s not in hist: continue
      if "h_tot" in hist: continue
      _up=File.Get(hist)
      up = _up.Clone("up_post")
      up.Sumw2()
      if up.Integral() == 0: continue
      if up.Integral() == postFit_original.Integral(): continue 
      nbins=up.GetSize()
      if normed:
        postFit.Scale(1/norm_factor)
        up.Scale(1/norm_factor)
      error = up.GetBinContent(binN)-postFit.GetBinContent(binN)
      errors.append(error)
  groomed_errors=errors
  total_error_list = map(lambda x: x**2,groomed_errors)
  total_error =  math.sqrt(sum(total_error_list))
  File.Close()
  return total_error

def getPreFitSystematicError(f,binN,channel,process,variable,norm_factor):
  File = ROOT.TFile(f,"r")
  ROOT.gROOT.cd()
  histograms= []
  errors = []
  for h in File.GetListOfKeys():
    histograms.append(h.GetName())
  if process=="signal":
     samples = [variable+"_ttphoton"]
  elif channel=="SL":
    samples = [variable+"_hadronfakes",variable+"_electronfakes",variable+"_Wphoton",variable+"_QCD",variable+"_Other"]
  elif channel=="DL":
    samples = [variable+"_hadronfakes",variable+"_electronfakes",variable+"_Zphoton",variable+"_Other"]
  for s in samples:
    for hist in histograms:
      if s not in hist: continue
      if "_orig" in hist: continue
      if "_regBin" in hist: continue
      if "Down" in hist: continue
      if "WphotonSF_Up" in hist:continue
      if "SigXsecOverSM" in hist: continue
      if "Shape_Up" in hist: continue
      preFit_original=File.Get(s)
      preFit=preFit_original.Clone("preFit_original")
      preFit_original.Sumw2()
      preFit.Sumw2()
      if hist == s: continue
      if "h_tot" in hist: continue
      error = 0
      _up=File.Get(hist)
      up = _up.Clone("up")
      up.Sumw2()
      if up.Integral() == 0: continue
      if up.Integral() == preFit_original.Integral(): continue
      nbins=up.GetSize()
      if normed:
        preFit.Scale(1/norm_factor)
        up.Scale(1/norm_factor)
      error = up.GetBinContent(binN)-preFit.GetBinContent(binN)
      errors.append(error)
  groomed_errors=errors
  total_error_list = map(lambda x: x**2,groomed_errors)
  total_error =  math.sqrt(sum(total_error_list))
  File.Close()
  return total_error

def plot(channel,ntuplePath,variable,xvar,process):
  ROOT.gROOT.cd()

  postFitFile=ntuplePath+variable+"_postFit.root"

  if channel=="SL":
    prefitNtuple="ejets_mujets_merged_"+variable+"_histos.root"
  else: 
    prefitNtuple="ee_mumu_emu_merged_"+variable+"_histos.root"
  preFitFile = ntuplePath+"/"+prefitNtuple

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

  print "Doing postFit correalted ", postFitFile
  _histo_postFit_correlated = drawPlots(postFitFile,process,channel,variable,ROOT.kBlue,"postfit")
  histo_postFit_correlated = _histo_postFit_correlated[0]
  histo_postFit_correlated_norm_factor = _histo_postFit_correlated[1]
  Max=histo_postFit_correlated.GetMaximum()
  if channel=="SL":
    if normed:
      histo_postFit_correlated.SetMaximum(Max+0.04) # If normalized
    else:
      histo_postFit_correlated.SetMaximum(Max+300)
  else:
    if normed:
      histo_postFit_correlated.SetMaximum(Max+0.05)
    else:
      histo_postFit_correlated.SetMaximum(Max+200)
  histo_postFit_correlated.DrawCopy("hist")
  histo_postFit_correlated.SetFillColorAlpha(ROOT.kBlue,alpha)
  histo_postFit_correlated.SetFillStyle(3353)
  histo_postFit_correlated.Draw("e2same ")

  stat_errors_from_prefit=[]
  print "Doing preFit uncorrelated ", preFitFile 
  _histo_preFit_UNcorrelated = drawPlots(preFitFile,process,channel,variable,ROOT.kGreen+2,"prefit")
  histo_preFit_UNcorrelated = _histo_preFit_UNcorrelated[0]
  histo_preFit_UNcorrelated_norm_factor=_histo_preFit_UNcorrelated[1]
  histo_preFit_UNcorrelated.SetLineColor(ROOT.kGreen+2)
  histo_preFit_UNcorrelated.DrawCopy("hist same")
  histo_preFit_UNcorrelated.SetFillColorAlpha(ROOT.kGreen+2,alpha)
  histo_preFit_UNcorrelated.SetLineColor(0)
  histo_preFit_UNcorrelated.SetFillStyle(3395)
  histo_preFit_UNcorrelated.Draw("e2same ")
  for b in range(1,histo_preFit_UNcorrelated.GetSize()-1):
    totalBinError = getPreFitSystematicError(preFitFile,b,channel,process,variable,histo_preFit_UNcorrelated_norm_factor)
    stat_error = histo_preFit_UNcorrelated.GetBinError(b)
    stat_errors_from_prefit.append(stat_error)
    error_with_stat = math.sqrt(totalBinError**2+stat_error**2)
    histo_preFit_UNcorrelated.SetBinError(b,0)
    histo_preFit_UNcorrelated.SetBinError(b,error_with_stat)

  print "Doing postFit uncorrelated ", postFitFile 
  _histo_postFit_UNcorrelated = drawPlots(postFitFile,process,channel,variable,ROOT.kRed,"postfit")
  histo_postFit_UNcorrelated = _histo_postFit_UNcorrelated[0] 
  histo_postFit_UNcorrelated_norm_factor = _histo_postFit_UNcorrelated[1] 
  histo_postFit_UNcorrelated.SetFillStyle(0)
  histo_postFit_UNcorrelated.DrawCopy("hist same")
  histo_postFit_UNcorrelated.SetFillColorAlpha(ROOT.kRed,alpha)
  histo_postFit_UNcorrelated.SetFillStyle(3335)
  histo_postFit_UNcorrelated.Draw("e2same ")
  for b in range(1,histo_postFit_UNcorrelated.GetSize()-1):
    totalBinError = getPostFitSystematicError(postFitFile,b,channel,process,variable,histo_postFit_UNcorrelated_norm_factor)
    error_with_stat = math.sqrt(totalBinError**2+stat_errors_from_prefit[b-1]**2)
    histo_postFit_UNcorrelated.SetBinError(b,0)
    histo_postFit_UNcorrelated.SetBinError(b,error_with_stat)

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
  total=histo_postFit_correlated.Clone("total")
  total.SetLineColor(ROOT.kBlack)
  leg.AddEntry(total,"Total "+process,"l");

  uncert_cor=histo_postFit_correlated.Clone("legend")
  uncert_cor.SetFillColor(ROOT.kBlue)
  uncert_cor.SetLineColor(0)
  uncert_uncor=histo_postFit_UNcorrelated.Clone("legend2")
  uncert_uncor.SetFillColor(ROOT.kRed)
  uncert_uncor.SetLineColor(0)

  uncert_uncor_prefit=histo_preFit_UNcorrelated.Clone("legend2")
  uncert_uncor_prefit.SetFillColor(ROOT.kGreen+2)
  uncert_uncor_prefit.SetLineColor(0)
  
  leg.AddEntry(uncert_uncor_prefit, "Uncorrelated "+process+" uncertainties (prefit)","f")
  leg.AddEntry(uncert_uncor,"Uncorrelated "+process+ " uncertaintes (postfit)","f")
  leg.AddEntry(uncert_cor,"Correlated "+process+" uncertainties (postfit)","f")
  leg.SetBorderSize(0)
  leg.SetFillStyle(0)
  leg.Draw()


   #Ratio plot
  pad2.cd()
  ratio1 = histo_postFit_correlated.Clone("ratio")
  ratio1.SetFillStyle(0)
  ratio1.SetStats(0)
  ratio1.Divide(histo_postFit_correlated)
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

  #line = ROOT.TF1("Sig_fa1","1",-1000,1000);
  #line.Draw("same")
  #line.SetLineColor(ROOT.kBlue);
  #line.SetLineStyle(2);

  # Not plot postFit Uncor/ postFit Corr
  ratio2 = histo_postFit_correlated.Clone("ratio_2")
  ratio2.Divide(histo_postFit_UNcorrelated)
  ratio2.SetLineColor(ROOT.kRed)
  fill=histo_postFit_UNcorrelated.GetFillStyle()
  ratio2.SetFillStyle(0)
  nbins=ratio2.GetSize()
  errors_2 = []
  for b in range(1,nbins-1):
    error_corr=histo_postFit_correlated.GetBinError(b)
    error_uncorr=histo_postFit_UNcorrelated.GetBinError(b)
    error = (error_uncorr)/(error_corr)
    print "ratio 2 = ", error
    errors_2.append(error)
    ratio2.SetBinContent(b,error)
  _max2=max(errors_2)
  _min2=min(errors_2)

  # Not plot preFit Uncor/ postFit Corr
  ratio3 = histo_postFit_correlated.Clone("ratio_3")
  ratio3.Divide(histo_preFit_UNcorrelated)
  ratio3.SetLineColor(ROOT.kGreen+2)
  ratio3.SetFillStyle(0)
  nbins=ratio3.GetSize()
  errors_3=[]
  for b in range(1,nbins-1):
    error_corr=histo_postFit_correlated.GetBinError(b)
    error_uncorr=histo_preFit_UNcorrelated.GetBinError(b)
    error = (error_uncorr)/(error_corr)
    print "ratio 3 = ", error
    errors_3.append(error)
    ratio3.SetBinContent(b,error)
  _max3=max(errors_3)
  _min3=min(errors_3)


  Max=max(_max2,_max3)
  Min=min(_min2,_min3)
  ratio1.SetMinimum(Min-0.5)
  ratio1.SetMaximum(Max+0.5)
  ratio1.SetLineColor(ROOT.kBlue)
  ratio1.SetLineStyle(2)
  ratio1.DrawCopy("hist ")
  ratio1.SetFillColorAlpha(ROOT.kBlue,alpha);
  fill=histo_postFit_correlated.GetFillStyle()
  ratio1.SetFillStyle(fill)

  ratio1.Draw("e2same")
  ratio2.Draw("same hist ")
  ratio3.Draw("same hist ")

  c1.SaveAs(variable+"_uncert_comparison_"+process+".pdf")


plot("SL",SL_path, "event_ELD_MVA_ejets","event level descriminator", "background")
plot("SL",SL_path, "event_ELD_MVA_ejets","event level descriminator", "background")
plot("SL",SL_path, "ph_pt_ejets","p_{T}(#gamma)", "background")
plot("SL",SL_path, "ph_eta_ejets","#eta(#gamma)","background")
plot("SL",SL_path, "dR_lept_ejets","#DeltaR(#gamma,l)","background")
#
plot("SL",SL_path, "event_ELD_MVA_ejets","event level descriminator", "signal")
plot("SL",SL_path, "ph_pt_ejets","p_{T}(#gamma)", "signal")
plot("SL",SL_path, "ph_eta_ejets","#eta(#gamma)","signal")
plot("SL",SL_path, "dR_lept_ejets","#DeltaR(#gamma,l)","signal")
#
plot("DL",DL_path, "dEta_lep_ee","#Delta#eta(l,l)","background")
plot("DL",DL_path, "dPhi_lep_ee","#Delta#phi(l,l)","background")
plot("DL",DL_path, "dR_lept_ee","#DeltaR(#gamma,l)","background")
plot("DL",DL_path, "event_ELD_MVA_ee","event level descriminator","background")
plot("DL",DL_path, "ph_pt_ee","p_{T}(#gamma)","background")
plot("DL",DL_path, "ph_eta_ee","#eta(#gamma)","background")
#
plot("DL",DL_path, "dEta_lep_ee","#Delta#eta(l,l)","signal")
plot("DL",DL_path, "dPhi_lep_ee","#Delta#phi(l,l)","signal")
plot("DL",DL_path, "dR_lept_ee","#DeltaR(#gamma,l)","signal")
plot("DL",DL_path, "event_ELD_MVA_ee","event level descriminator","signal")
plot("DL",DL_path, "ph_pt_ee","p_{T}(#gamma)","signal")
plot("DL",DL_path, "ph_eta_ee","#eta(#gamma)","signal")
#
